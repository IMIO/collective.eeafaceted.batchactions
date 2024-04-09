# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective.eeafaceted.batchactions.interfaces import IBatchActionsMarker
from collective.eeafaceted.batchactions.tests.base import BaseTestCase
from collective.eeafaceted.batchactions.tests.interfaces import IBatchActionsSpecificMarker
from plone import api
from plone.app.testing import login
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
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

    def test_viewlet_available(self):
        """Available by default."""
        viewlet = self._get_viewlet(self.eea_folder)
        self.assertTrue(viewlet.available())

    def test_viewlet_select_item_name(self):
        """Name of the CheckboxColumn."""
        viewlet = self._get_viewlet(self.eea_folder)
        self.assertEqual(viewlet.select_item_name, 'select_item')

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
        alsoProvides(folder, IBatchActionsMarker)
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
        alsoProvides(self.eea_folder, IBatchActionsSpecificMarker)
        self.assertEqual(
            viewlet._get_marker_interfaces(),
            [IBatchActionsMarker, IBatchActionsSpecificMarker])

    def test_get_batch_actions(self):
        """This will return every found action names.
           We test here classical functionnality with actions registered for IBatchActionsMarker."""
        viewlet = self._get_viewlet(self.eea_folder)
        self.assertEqual(
            viewlet.get_batch_actions(),
            [{'name': 'transition-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 10},
             {'name': 'labels-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 20},
             {'name': 'contact-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 30},
             {'name': 'testing-aruo-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 100}])
        # returned action names are traversable to get the form
        for action in viewlet.get_batch_actions():
            form = self.eea_folder.restrictedTraverse(action['name'])
            self.assertEqual(form.__name__, action['name'])
        # as zope admin
        login(self.portal.aq_parent, "admin")
        self.assertEqual(
            sorted([dic['name'] for dic in viewlet.get_batch_actions()]),
            ['contact-batch-action', 'delete-batch-action', 'labels-batch-action', 'testing-aruo-batch-action',
             'transition-batch-action', 'update-wf-role-mappings-batch-action'])

    def test_get_batch_actions_available(self):
        """A method 'available' is evaluated on the action view to check if it is available on context."""
        # mark eea_folder with IBatchActionsSpecificMarker so testing-batch-action is useable
        alsoProvides(self.eea_folder, IBatchActionsSpecificMarker)
        viewlet = self._get_viewlet(self.eea_folder)
        self.assertTrue('testing-batch-action' in [action['name'] for action in viewlet.get_batch_actions()])
        # 'testing-batch-action' is available if value 'hide_testing_action' not found in request
        self.request.set('hide_testing_action', True)
        self.assertFalse('testing-batch-action' in [action['name'] for action in viewlet.get_batch_actions()])
        # trying to execute a not available action will raise Unauthorized
        testing_form = getMultiAdapter((self.eea_folder, self.request), name=u'testing-batch-action')
        self.assertRaises(Unauthorized, testing_form)

    def test_get_batch_actions_consider_new_action_specific_interface(self):
        """Register a view for IBatchActionsSpecificMarker, get_batch_actions will
           behave differently if context implementing interface or not."""
        folder = api.content.create(
            type='Folder',
            id='folder',
            title='Folder',
            container=self.portal
        )
        alsoProvides(folder, IBatchActionsMarker)
        viewlet = self._get_viewlet(folder)
        self.assertEqual(
            viewlet.get_batch_actions(),
            [{'button_with_icon': False, 'name': 'transition-batch-action', 'weight': 10, 'overlay': True},
             {'button_with_icon': False, 'name': 'labels-batch-action', 'weight': 20, 'overlay': True},
             {'button_with_icon': False, 'name': 'contact-batch-action', 'weight': 30, 'overlay': True},
             {'button_with_icon': False, 'name': 'testing-aruo-batch-action', 'weight': 100, 'overlay': True}])

        # mark with IBatchActionsSpecificMarker
        alsoProvides(folder, IBatchActionsSpecificMarker)
        self.assertEqual(
            viewlet.get_batch_actions(),
            [{'name': 'transition-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 10},
             {'name': 'labels-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 20},
             {'name': 'contact-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 30},
             {'name': 'testing-aruo-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 100},
             {'name': 'testing-batch-action', 'button_with_icon': True, 'overlay': False, 'weight': 100}])
        # returned action names are traversable to get the form
        for action in viewlet.get_batch_actions():
            form = folder.restrictedTraverse(action['name'])
            self.assertEqual(form.__name__, action['name'])

        # still correct on eea_folder that does not implements IBatchActionsSpecificMarker
        viewlet = self._get_viewlet(self.eea_folder)
        self.assertEqual(
            viewlet.get_batch_actions(),
            [{'name': 'transition-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 10},
             {'name': 'labels-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 20},
             {'name': 'contact-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 30},
             {'name': 'testing-aruo-batch-action', 'button_with_icon': False, 'overlay': True, 'weight': 100}])
