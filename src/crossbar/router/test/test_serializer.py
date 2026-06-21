#####################################################################################
#
#  Copyright (c) typedef int GmbH
#  SPDX-License-Identifier: EUPL-1.2
#
#####################################################################################

from unittest import skipUnless

import txaio

txaio.use_twisted()  # noqa

from autobahn.wamp import message
from autobahn.wamp.serializer import (
    CBORSerializer,
    FlatBuffersSerializer,
    JsonSerializer,
    MsgPackSerializer,
)
from twisted.trial import unittest

from crossbar.router.protocol import WampRawSocketServerFactory

# UBJSON is optional: it is backed by bjdata, a CPython-only autobahn dependency
# (unavailable on PyPy). Import it defensively so this test exercises it where
# present and skips it where not.
try:
    from autobahn.wamp.serializer import UBJSONSerializer

    _HAS_UBJSON = True
except ImportError:
    _HAS_UBJSON = False


class TestWampSerializerRoundtrip(unittest.TestCase):
    """
    Round-trip tests for the WAMP serializers Crossbar.io relies on.

    These guard that the serializers actually load and (de)serialize on the
    running interpreter. Because Crossbar.io must run on both CPython AND PyPy,
    the CI matrix runs these on both - which is where backend differences (e.g.
    a serializer backend that is CPython-only) surface. See issue #2224.
    """

    def setUp(self):
        # a representative WAMP message with positional and keyword payload
        self.msg = message.Event(
            subscription=123,
            publication=456,
            args=[1, "two", 3.0, True, None],
            kwargs={"key": "value", "nested": [1, 2, 3]},
        )

    def _roundtrip(self, serializer):
        data, _is_binary = serializer.serialize(self.msg)
        messages = serializer.unserialize(data)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], self.msg)

    def test_json(self):
        self._roundtrip(JsonSerializer())

    def test_msgpack(self):
        self._roundtrip(MsgPackSerializer())

    def test_cbor(self):
        self._roundtrip(CBORSerializer())

    def test_flatbuffers(self):
        self._roundtrip(FlatBuffersSerializer())

    @skipUnless(_HAS_UBJSON, "UBJSON serializer unavailable (bjdata is CPython-only)")
    def test_ubjson(self):
        self._roundtrip(UBJSONSerializer())


class TestServerFactorySerializerSelection(unittest.TestCase):
    """
    Tests for the transport serializer selection in the server factories.

    A transport may list a serializer that is unavailable on the running
    interpreter (e.g. UBJSON, whose bjdata backend is CPython-only and absent on
    PyPy). Such a recognized-but-unavailable serializer must be skipped
    gracefully (warning logged), NOT abort transport startup - while a genuinely
    unknown serializer name (a typo) must still be rejected. See issue #2224.
    """

    class _DummySessionFactory:
        # the serializer selection runs before the WAMP session factory is used
        pass

    def test_unavailable_serializer_is_skipped(self):
        # full default serializer set, as used by the autobahn examples router
        # config; on PyPy "ubjson" is unavailable and must be skipped rather than
        # raising "invalid WAMP serializers specified (... unprocessed)".
        factory = WampRawSocketServerFactory(
            self._DummySessionFactory(),
            {"serializers": ["cbor", "msgpack", "ubjson", "json"]},
        )
        # at least the interpreter-independent serializers must have been loaded
        self.assertTrue(factory._serializers)

    def test_unknown_serializer_is_rejected(self):
        with self.assertRaises(Exception) as ctx:
            WampRawSocketServerFactory(
                self._DummySessionFactory(),
                {"serializers": ["cbor", "not_a_serializer"]},
            )
        self.assertIn("not_a_serializer", str(ctx.exception))
