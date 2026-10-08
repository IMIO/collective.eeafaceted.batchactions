# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.eeafaceted.batchactions import _
from collective.eeafaceted.batchactions.testing import INTEGRATION  # noqa
from plone import api
from plone.base.interfaces import INonInstallable
from plone.base.utils import get_installer
from zope.component import getUtility
from zope.i18n import translate

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.eeafaceted.batchactions is properly installed."""

    layer = INTEGRATION

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal)

    def test_product_installed(self):
        """Test if collective.eeafaceted.batchactions is installed."""
        self.assertTrue(
            self.installer.is_product_installed("collective.eeafaceted.batchactions")
        )

    def test_uninstall(self):
        """Test if collective.eeafaceted.batchactions is cleanly uninstalled."""
        self.installer.uninstall_product("collective.eeafaceted.batchactions")
        self.assertFalse(
            self.installer.is_product_installed("collective.eeafaceted.batchactions")
        )
        self.assertIsNone(
            api.portal.get_registry_record(
                "plone.bundles/collective.eeafaceted.batchactions.jscompilation",
                default=None,
            )
        )

    def test_resources_registered(self):
        """batch_actions.css and .js are registered by the default profile, after the bundles they use."""
        prefix = "plone.bundles/collective.eeafaceted.batchactions."
        self.assertEqual(
            api.portal.get_registry_record(prefix + "csscompilation"),
            "++resource++collective.eeafaceted.batchactions/batch_actions.css",
        )
        self.assertEqual(
            api.portal.get_registry_record(prefix + "jscompilation"),
            "++resource++collective.eeafaceted.batchactions/batch_actions.js",
        )
        self.assertEqual(
            api.portal.get_registry_record(prefix + "depends"),
            "plone,faceted-z3ctable,imio-helpers",
        )
        # the bundles it depends on are installed (a missing one would drop it from the page)
        for name in ("faceted-z3ctable", "imio-helpers"):
            self.assertTrue(
                api.portal.get_registry_record(
                    "plone.bundles/{}.jscompilation".format(name), default=None
                )
            )

    def test_hidden_profiles(self):
        """The uninstall profile is hidden from the site creation and add-ons screens."""
        hidden = getUtility(INonInstallable, name="collective.eeafaceted.batchactions")
        self.assertEqual(
            hidden.getNonInstallableProfiles(),
            ["collective.eeafaceted.batchactions:uninstall"],
        )

    def test_translations(self):
        """The fr translations are registered (locales)."""
        self.assertEqual(
            translate(
                u"transition-batch-action-but",
                domain="collective.eeafaceted.batchactions",
                target_language="fr",
            ),
            u"Changer l'\xe9tat",
        )
        self.assertEqual(
            translate(_(u"Batch state change"), target_language="fr"),
            u"Changer l'\xe9tat par lot",
        )
