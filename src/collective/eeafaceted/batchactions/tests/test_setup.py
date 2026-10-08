# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.eeafaceted.batchactions import _
from collective.eeafaceted.batchactions.testing import INTEGRATION  # noqa
from imio.helpers import HAS_PLONE_6_AND_MORE
from zope.i18n import translate

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

    def _resource_ids(self):
        """Ids of the registered css and js resources."""
        if HAS_PLONE_6_AND_MORE:
            self.skipTest("Plone 6: read the plone.bundles registry records (phase 7)")
        return list(self.portal.portal_css.getResourceIds()) + list(self.portal.portal_javascripts.getResourceIds())

    def test_resources_registered(self):
        """batch_actions.css and .js are registered by the default profile."""
        resource_ids = self._resource_ids()
        self.assertIn("++resource++collective.eeafaceted.batchactions/batch_actions.css", resource_ids)
        self.assertIn("++resource++collective.eeafaceted.batchactions/batch_actions.js", resource_ids)

    def test_translations(self):
        """The fr translations are registered (locales)."""
        self.assertEqual(
            translate(u"transition-batch-action-but", domain="collective.eeafaceted.batchactions",
                      target_language="fr"),
            u"Changer l'\xe9tat")
        self.assertEqual(translate(_(u"Batch state change"), target_language="fr"), u"Changer l'\xe9tat par lot")
