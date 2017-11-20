# -*- coding: utf-8 -*-

# from collective.eeafaceted.batchactions.browser.viewlets import BatchActionsViewlet
from collective.eeafaceted.batchactions.interfaces import IBatchActionsMarker
from collective.eeafaceted.batchactions.tests.base import BaseTestCase
from collective.eeafaceted.batchactions.tests.interfaces import IBatchActionsSpecificMarker
from plone import api
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.interface import directlyProvides
from zope.viewlet.interfaces import IViewletManager


class TestViewlets(BaseTestCase):

    def _get_viewlet_manager(self, context):
        """ """
        view = BrowserView(self.eea_folder, self.request)
        manager_name = 'collective.eeafaceted.z3ctable.bottomabovenav'
        viewlet_manager = getMultiAdapter(
            (context, self.request, view),
            IViewletManager,
            manager_name)
        viewlet_manager.update()
        return viewlet_manager

    def _get_viewlet(self, context):
        """ """
        viewlet_manager = self._get_viewlet_manager(context)
        viewlet = viewlet_manager.get(u'collective.eeafaceted.batchactions')
        return viewlet

    def test_viewlet_only_rendered_on_IBatchActionsMarker(self):
        """ """
        folder = api.content.create(
            type='Folder',
            id='folder',
            title='Folder',
            container=self.portal
        )
        viewlet = self._get_viewlet(folder)
        self.assertIsNone(viewlet)
        directlyProvides(folder, IBatchActionsMarker)
        viewlet = self._get_viewlet(folder)
        self.assertEqual(viewlet.__name__, u'collective.eeafaceted.batchactions')

    def test_get_marker_interfaces(self):
        """_get_marker_interfaces will return the marker interfaces views
           may be registered for.  It is the IBatchActionsMarker and others
           inheriting from it."""
        viewlet = self._get_viewlet(self.eea_folder)
        # the u'collective.eeafaceted.batchactions' viewlet exists in the viewlet manager
        # as IBatchActionsMarker is implemented by self.eea_folder
        self.assertEqual(viewlet.__name__, u'collective.eeafaceted.batchactions')
        self.assertEqual(viewlet._get_marker_interfaces(), [IBatchActionsMarker])

        # if an interface suclassing IBatchActionsMarker is found, it is also returned
        directlyProvides(self.eea_folder, IBatchActionsSpecificMarker)
        self.assertEqual(
            viewlet._get_marker_interfaces(),
            [IBatchActionsMarker, IBatchActionsSpecificMarker])

    def test_get_batch_action_names(self):
        """This will return every found action names.
           We test here classical functionnality with actions registered for IBatchActionsMarker."""
        viewlet = self._get_viewlet(self.eea_folder)
        self.assertEqual(
            viewlet.get_batch_action_names(),
            set(['transition-batch-action']))

        # returned action names are traversable to get the form
        for action_name in viewlet.get_batch_action_names():
            form = self.eea_folder.restrictedTraverse(action_name)
            self.assertEqual(form.__name__, action_name)

    def test_get_batch_action_names_consider_new_action_specific_interface(self):
        """Register a view for IBatchActionsSpecificMarker, get_batch_action_names will
           behave differently if context implementing interface or not."""
        folder = api.content.create(
            type='Folder',
            id='folder',
            title='Folder',
            container=self.portal
        )
        directlyProvides(folder, IBatchActionsMarker)
        viewlet = self._get_viewlet(folder)
        self.assertEqual(
            viewlet.get_batch_action_names(),
            set(['transition-batch-action']))

        # mark with IBatchActionsSpecificMarker
        directlyProvides(folder, IBatchActionsSpecificMarker)
        self.assertEqual(
            viewlet.get_batch_action_names(),
            set(['testing-batch-action', 'transition-batch-action']))
        # returned action names are traversable to get the form
        for action_name in viewlet.get_batch_action_names():
            form = folder.restrictedTraverse(action_name)
            self.assertEqual(form.__name__, action_name)

        # still correct on eea_folder that does not implements IBatchActionsSpecificMarker
        viewlet = self._get_viewlet(self.eea_folder)
        self.assertEqual(
            viewlet.get_batch_action_names(),
            set(['transition-batch-action']))
