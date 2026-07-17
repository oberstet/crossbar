#####################################################################################
#
#  Copyright (c) typedef int GmbH
#  SPDX-License-Identifier: EUPL-1.2
#
#####################################################################################

import txaio

txaio.use_twisted()  # noqa

from autobahn.twisted.rawsocket import WampRawSocketServerFactory
from autobahn.twisted.websocket import WebSocketClientFactory, WebSocketServerFactory
from twisted.trial import unittest

from crossbar.router.protocol import set_rawsocket_options, set_websocket_options

# 16 MB: the secure-by-default receive limit for both transports. It is the
# largest value a WAMP RawSocket can negotiate (the handshake length exponent
# tops out at 2**(9+15)), so it is the largest value common to both transports.
DEFAULT_MAX_MESSAGE_SIZE = 2**24


class DefaultMaxMessageSizeTests(unittest.TestCase):
    """
    A transport that does not set ``max_message_size`` explicitly must default
    to 16 MB on BOTH WebSocket and RawSocket (crossbar #2251). Historically the
    WebSocket default was ``0`` (unlimited), disagreeing with RawSocket's 16 MB
    and leaving the router unbounded by default.
    """

    def test_websocket_server_default_is_16mb(self):
        factory = WebSocketServerFactory()
        set_websocket_options(factory, {})
        self.assertEqual(factory.maxMessagePayloadSize, DEFAULT_MAX_MESSAGE_SIZE)

    def test_websocket_client_default_is_16mb(self):
        factory = WebSocketClientFactory()
        set_websocket_options(factory, {})
        self.assertEqual(factory.maxMessagePayloadSize, DEFAULT_MAX_MESSAGE_SIZE)

    def test_rawsocket_server_default_is_16mb(self):
        factory = WampRawSocketServerFactory(lambda: None)
        set_rawsocket_options(factory, {})
        self.assertEqual(factory._max_message_size, DEFAULT_MAX_MESSAGE_SIZE)

    def test_both_transports_agree_on_default(self):
        ws = WebSocketServerFactory()
        set_websocket_options(ws, {})
        rs = WampRawSocketServerFactory(lambda: None)
        set_rawsocket_options(rs, {})
        self.assertEqual(ws.maxMessagePayloadSize, rs._max_message_size)

    def test_explicit_websocket_value_is_honored(self):
        # An explicit setting must still win over the new default (regression
        # guard: the default change must not clobber configured values).
        factory = WebSocketServerFactory()
        set_websocket_options(factory, {"max_message_size": 4096})
        self.assertEqual(factory.maxMessagePayloadSize, 4096)
