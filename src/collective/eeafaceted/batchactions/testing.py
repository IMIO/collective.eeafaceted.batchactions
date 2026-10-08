# -*- coding: utf-8 -*-
"""Base module for unittesting."""
from collective.eeafaceted.batchactions.browser.views import TransitionBatchActionForm
from collective.eeafaceted.batchactions.interfaces import IBatchActionsMarker
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from plone import api
from plone.app.robotframework.remote import RemoteLibrary
from plone.app.robotframework.remote import RemoteLibraryLayer
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.robotframework.utils import disableCSRFProtection
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
from zope.dottedname.resolve import resolve
from zope.globalrequest import setLocal
from zope.interface import alsoProvides

import collective.eeafaceted.batchactions
import pkg_resources


try:
    from plone.testing.zope import WSGI_SERVER_FIXTURE as SERVER_FIXTURE
except ImportError:  # Plone 4
    from plone.testing.z2 import ZSERVER_FIXTURE as SERVER_FIXTURE


try:
    pkg_resources.get_distribution("plone.app.contenttypes")
except pkg_resources.DistributionNotFound:
    HAS_PA_CONTENTTYPES = False
else:
    HAS_PA_CONTENTTYPES = True


class NakedPloneLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    products = ("collective.eeafaceted.batchactions", "eea.facetednavigation")

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=collective.eeafaceted.batchactions, name="testing.zcml")
        for p in self.products:
            z2.installProduct(app, p)
        if HAS_PA_CONTENTTYPES:
            import plone.app.contenttypes

            self.loadZCML(package=plone.app.contenttypes)

    def tearDownZope(self, app):
        """Tear down Zope."""
        pass


NAKED_PLONE_FIXTURE = NakedPloneLayer(name="NAKED_PLONE_FIXTURE")

NAKED_PLONE_INTEGRATION = IntegrationTesting(
    bases=(NAKED_PLONE_FIXTURE,), name="NAKED_PLONE_INTEGRATION"
)


class CollectiveEeafacetedBatchActionsLayer(NakedPloneLayer):
    def setUpPloneSite(self, portal):
        """Set up Plone."""
        setLocal("request", portal.REQUEST)
        # Install into Plone site using portal_setup
        applyProfile(portal, "collective.eeafaceted.batchactions:testing")

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        # make sure we have a default workflow
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")

        # pac is really installed ?
        if (
            HAS_PA_CONTENTTYPES
            and portal.portal_setup.getLastVersionForProfile(
                "plone.app.contenttypes:default"
            )
            != "unknown"
        ):
            self.applyProfile(portal, "plone.app.contenttypes:default")


FIXTURE = CollectiveEeafacetedBatchActionsLayer(name="FIXTURE")


INTEGRATION = IntegrationTesting(bases=(FIXTURE,), name="INTEGRATION")


FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,), name="FUNCTIONAL")


class LabelsLayer(PloneSandboxLayer):
    """Optional ftw.labels integration (LabelsBatchActionForm)."""

    defaultBases = (FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(
            package=collective.eeafaceted.batchactions, name="testing_labels.zcml"
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, "ftw.labels:default")


LABELS_FIXTURE = LabelsLayer(name="LABELS_FIXTURE")

LABELS_FUNCTIONAL = FunctionalTesting(bases=(LABELS_FIXTURE,), name="LABELS_FUNCTIONAL")


class ContactLayer(PloneSandboxLayer):
    """Optional collective.contact.core/widget integration (ContactBaseBatchActionForm)."""

    defaultBases = (FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(
            package=collective.eeafaceted.batchactions, name="testing_contact.zcml"
        )

    def setUpPloneSite(self, portal):
        setLocal("request", portal.REQUEST)
        applyProfile(portal, "collective.contact.core:test_data")


CONTACT_FIXTURE = ContactLayer(name="CONTACT_FIXTURE")

CONTACT_FUNCTIONAL = FunctionalTesting(
    bases=(CONTACT_FIXTURE,), name="CONTACT_FUNCTIONAL"
)


class IRobotBatchActionsMarker(IBatchActionsMarker):
    """Robot folder also showing the no-overlay-transition-batch-action (testing.zcml)."""


class NoOverlayTransitionBatchActionForm(TransitionBatchActionForm):
    """The transition action opened as a page."""

    overlay = False


class BatchActionsKeywords(RemoteLibrary):
    def enable_faceted_table(self, path, marker=""):
        """Faceted navigation with the faceted-table-items layout on the folder at path
        (from the site), providing the marker interface (dotted name) if any."""
        disableCSRFProtection()
        folder = api.content.get(path=path)
        if marker:
            alsoProvides(folder, resolve(marker))
        folder.unrestrictedTraverse("@@faceted_subtyper").enable()
        IFacetedLayout(folder).update_layout("faceted-table-items")
        folder.reindexObject()
        # enable() redirects: answer the XML-RPC call
        self.REQUEST.response.setStatus(200)


REMOTE_LIBRARY_FIXTURE = RemoteLibraryLayer(
    bases=(PLONE_FIXTURE,),
    libraries=REMOTE_LIBRARY_BUNDLE_FIXTURE.libraryBases[1:] + (BatchActionsKeywords,),
    name="BatchActionsRemoteLibrary:RobotRemote",
)


ACCEPTANCE = FunctionalTesting(
    bases=(FIXTURE, REMOTE_LIBRARY_FIXTURE, SERVER_FIXTURE), name="ACCEPTANCE"
)
