# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.eeafaceted.batchactions.testing import INTEGRATION  # noqa
from imio.helpers import HAS_PLONE_6_AND_MORE

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.eeafaceted.batchactions is properly installed."""

    layer = INTEGRATION

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        if HAS_PLONE_6_AND_MORE:
            from plone.base.utils import get_installer
            self.installer = get_installer(self.portal)

    def test_product_installed(self):
        """Test if collective.eeafaceted.batchactions is installed."""
        if HAS_PLONE_6_AND_MORE:
            self.assertTrue(self.installer.is_product_installed("collective.eeafaceted.batchactions"))

    def test_uninstall(self):
        """Test if collective.eeafaceted.batchactions is cleanly uninstalled."""
        if HAS_PLONE_6_AND_MORE:
            self.installer.uninstall_product("collective.eeafaceted.batchactions")
            self.assertFalse(self.installer.is_product_installed("collective.eeafaceted.batchactions"))
