##############################################################################
#
#  Copyright (C) Tavendo GmbH. All rights reserved.
#
###############################################################################

from __future__ import print_function
from __future__ import absolute_import

from autobahn.wamp import types
from autobahn.twisted.component import Component
from autobahn.twisted.util import sleep
from autobahn.websocket.compress import PerMessageDeflateOffer, \
    PerMessageDeflateResponse, \
    PerMessageDeflateResponseAccept
from twisted.internet.defer import Deferred, inlineCallbacks

import pytest

# do not directly import fixtures, or session-scoped ones will get run
# twice.
from ..helpers import *
from ..helpers import _create_temp, _cleanup_crossbar


# The router transport dedicated to this test (see conftest.py,
# "ws_test_zipbomb"): permessage-deflate is enabled ON THE ROUTER and
# max_message_size is set to 1500 octets.
#
# Enabling deflate router-side is essential and was the bug in the previous
# version of this test (#2250): it configured compression only on the *client*,
# so the router declined the offers, nothing was ever compressed, and the
# "zip bomb" travelled uncompressed. It then tripped max_frame_payload_size - an
# unrelated, ordinary wire-size check - and the test passed without ever
# exercising decompression at all.
ZIPBOMB_URL = u"ws://localhost:6566/ws"

# The router's configured max_message_size (uncompressed / application level).
ROUTER_MAX_MESSAGE_SIZE = 1500

# Deflates to a few dozen octets on the wire, but inflates to ~20k - i.e. tiny
# compressed, far past ROUTER_MAX_MESSAGE_SIZE once inflated. This is the whole
# point: the compressed frame is small enough that no frame-size check can fire,
# so the only mechanism that can reject it is enforcement against the
# UNCOMPRESSED reassembled size (autobahn-python #1909 / GHSA-hxp9-w8x3-p566).
BOMB = u"a" * 20000

# Comfortably under the cap - used as a control, to prove the transport works
# and that having compression on does not break ordinary traffic.
SMALL = u"a" * 20


def _compressed_transport(url):
    """
    A client transport that offers permessage-deflate. The router must accept
    the offer for anything to actually be compressed.
    """
    offers = [PerMessageDeflateOffer()]

    def accept(response):
        if isinstance(response, PerMessageDeflateResponse):
            return PerMessageDeflateResponseAccept(response)

    return {
        u"url": url,
        u"options": {
            u"per_message_compression_offers": offers,
            u"per_message_compression_accept": accept,
        },
    }


@inlineCallbacks
def test_router_rejects_zip_bomb(reactor, crossbar):
    """
    The ROUTER must reject a decompression bomb.

    A client publishes a payload that is small on the wire but inflates far past
    the router's configured max_message_size. The router must reject it (close
    code 1009, MESSAGE_TOO_BIG) and drop that client's connection.

    This asserts Crossbar's own guard - what operators configure
    max_message_size for - rather than a client-side limit.

    What makes this a *clean* assertion: the compressed frame is only a few
    dozen octets, so no frame-size limit can possibly fire. The only mechanism
    that can drop this connection is enforcement against the uncompressed
    reassembled size. Verified to be a genuine regression test: against an
    autobahn without that fix (< 26.7.1) the router checks the compressed size,
    accepts the bomb and never drops, and this test fails.

    NOTE (#2250): a client-side counterpart - subscriber bounds the decompressed
    size itself, publisher sends a bomb through an uncapped router - was tried
    and deliberately dropped. It cannot discriminate at this level: it passes
    against both a fixed and an unfixed autobahn, because the connection drops
    either way (cleanly via PayloadExceededError when fixed; via a zlib decode
    error on truncated data when not). Telling those apart needs protocol-level
    introspection the component API does not expose, and a test that passes
    regardless of the fix is worse than none - it was exactly the flaw this
    issue was filed about. That path is properly covered at unit level by
    autobahn's PerMessageDeflateMaxMessageSizeTests (#1908), where the
    distinction is observable.
    """
    component = Component(
        transports=[_compressed_transport(ZIPBOMB_URL)],
        realm=u"functest_realm1",
    )

    dropped = Deferred()
    published_small = Deferred()
    joins = [0]

    @component.on_join
    @inlineCallbacks
    def go(session, details):
        joins[0] += 1
        if joins[0] > 1:
            # the component reconnects after the router drops us; don't re-send
            return
        # control: a small message must go through fine
        yield session.publish(
            u"foo", SMALL, options=types.PublishOptions(acknowledge=True)
        )
        published_small.callback(None)

        # the bomb: the router must reject this on its uncompressed size. We may
        # or may not get an error back here (the router aborts the connection),
        # so failures are expected and swallowed - the assertion is the drop.
        try:
            yield session.publish(
                u"foo", BOMB, options=types.PublishOptions(acknowledge=True)
            )
        except Exception:
            pass

    @component.on_disconnect
    def gone(session, was_clean=False):
        if not dropped.called:
            dropped.callback(was_clean)

    timeout = sleep(15)
    component.start(reactor)
    yield DeferredList(
        [timeout, dropped], fireOnOneErrback=True, fireOnOneCallback=True
    )

    assert published_small.called, "the small control message should have been accepted"
    assert not timeout.called, "shouldn't time out"
    assert dropped.called, (
        "the router should have dropped the connection: a message inflating to "
        "{} octets exceeds the router's max_message_size of {}".format(
            len(BOMB), ROUTER_MAX_MESSAGE_SIZE
        )
    )
