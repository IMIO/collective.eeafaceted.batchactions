# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2

import collective.eeafaceted.batchactions


class NakedPloneLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    products = ('collective.eeafaceted.batchactions', 'eea.facetednavigation')

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=collective.eeafaceted.batchactions,
                      name='testing.zcml')
        for p in self.products:
            z2.installProduct(app, p)

    def tearDownZope(self, app):
        """Tear down Zope."""
        pass

NAKED_PLONE_FIXTURE = NakedPloneLayer(
    name="NAKED_PLONE_FIXTURE"
)

NAKED_PLONE_INTEGRATION = IntegrationTesting(
    bases=(NAKED_PLONE_FIXTURE,),
    name="NAKED_PLONE_INTEGRATION"
)


class CollectiveEeafacetedBatchActionsLayer(NakedPloneLayer):

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'collective.eeafaceted.batchactions:testing')

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        # make sure we have a default workflow
        portal.portal_workflow.setDefaultChain('simple_publication_workflow')


FIXTURE = CollectiveEeafacetedBatchActionsLayer(
    name="FIXTURE"
)


INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,),
    name="INTEGRATION"
)


FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,),
    name="FUNCTIONAL"
)


ACCEPTANCE = FunctionalTesting(bases=(FIXTURE,
                                      REMOTE_LIBRARY_BUNDLE_FIXTURE,
                                      z2.ZSERVER_FIXTURE),
                               name="ACCEPTANCE")
