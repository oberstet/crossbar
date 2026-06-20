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
