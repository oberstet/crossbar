#####################################################################################
#
#  Copyright (c) typedef int GmbH
#  SPDX-License-Identifier: EUPL-1.2
#
#####################################################################################

from twisted.trial import unittest

from crossbar.node.main import _get_versions


class TestVersions(unittest.TestCase):
    """
    Tests for the software version reporting used by ``crossbar version``.
    """

    def test_lmdb_version_reported(self):
        """
        The LMDB version must be reported via the CFFI binding vendored in
        zlmdb (crossbar has no top-level "lmdb" dependency, so a top-level
        ``import lmdb`` is absent on a clean install and left the line blank).
        See #2156.
        """
        # the installed reactor is only read for its class name by _get_versions
        from twisted.internet import reactor

        v = _get_versions(reactor)

        self.assertTrue(v.lmdb_ver, "LMDB version is empty")
        # format is "<binding-version>/lmdb-<C-library-version>"
        self.assertIn("lmdb-", v.lmdb_ver)

    def test_zlmdb_version_reported(self):
        """
        zlmdb (which vendors the LMDB binding crossbar uses) must also be
        reported.
        """
        from twisted.internet import reactor

        v = _get_versions(reactor)

        self.assertTrue(v.zlmdb_ver, "zlmdb version is empty")
