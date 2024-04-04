# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective.eeafaceted.batchactions.browser.views import BaseBatchActionForm
from collective.eeafaceted.batchactions.tests.base import BaseTestCase
from imio.helpers.catalog import addOrUpdateIndexes
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFCore.permissions import AccessContentsInformation
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.permissions import View
from Products.CMFCore.utils import _checkPermission
from zope.component import getMultiAdapter


class TestActions(BaseTestCase):

    def setUp(self):
        """ """
        super(TestActions, self).setUp()
        self.doc1 = api.content.create(
            type='Document',
            id='doc1',
            title='Document 1',
            container=self.portal
        )
        self.doc2 = api.content.create(
            type='Document',
            id='doc2',
            title='Document 2',
            container=self.portal
        )

    def test_transition_action_apply(self):
        """Working behavior, we have several documents with same transition available."""
        # set 'uids' in form
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('transition-batch-action')
        # common transitions are shown, here it is the case as docs are in same state
        form.update()
        self.assertEqual(
            form.widgets['transition'].terms.terms.by_token.keys(),
            ['publish', 'submit'])
        form.request['form.widgets.transition'] = 'publish'
        extracted_data, errors = form.extractData()
        self.assertEqual(
            extracted_data,
            {'comment': None,
             'transition': 'publish',
             'referer': None,
             'uids': doc_uids}, ())

        # for now both docs are 'private'
        self.assertEqual(
            [api.content.get_state(self.doc1), api.content.get_state(self.doc2)],
            ['private', 'private'])
        form.handleApply(form, None)
        self.assertEqual(
            [api.content.get_state(self.doc1), api.content.get_state(self.doc2)],
            ['published', 'published'])

    def test_transition_action_cancel(self):
        """When cancelled, nothing is done and user is redirected to referer."""
        form = getMultiAdapter((self.eea_folder, self.request), name='transition-batch-action')
        self.request['HTTP_REFERER'] = self.portal.absolute_url()
        self.request.RESPONSE.status = 200
        self.assertNotEqual(
            self.request.RESPONSE.getHeader('location'),
            self.request['HTTP_REFERER'])
        form.handleCancel(form, None)
        self.assertEqual(self.request.RESPONSE.status, 302)
        self.assertEqual(
            self.request.RESPONSE.getHeader('location'),
            self.request['HTTP_REFERER'])

    def test_transition_action_uids_can_be_defined_on_request_or_form(self):
        """'uids' used by the form are retrieved no matter it is defined on
            self.request or self.request.form."""
        # set 'uids' in self.request.form
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('transition-batch-action')
        # common transitions are shown, here it is the case as docs are in same state
        form.update()
        extracted_data, errors = form.extractData()
        self.assertEqual(
            extracted_data['uids'], doc_uids)
        del self.request.form['form.widgets.uids']

        # set 'uids' in self.request
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request['uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('transition-batch-action')
        # common transitions are shown, here it is the case as docs are in same state
        form.update()
        extracted_data, errors = form.extractData()
        self.assertEqual(
            extracted_data['uids'], doc_uids)

    def test_transition_action_only_list_common_transitions(self):
        """Only work if there are common transitions for selected elements."""
        # set 'uids' in form
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('transition-batch-action')
        # common transitions are shown, here it is the case as docs are in same state
        form.update()
        self.assertEqual(
            form.widgets['transition'].terms.terms.by_token.keys(),
            ['publish', 'submit'])

        # change state of doc1, no common transition available
        api.content.transition(self.doc1, 'publish')
        form = self.eea_folder.restrictedTraverse('transition-batch-action')
        form.update()
        self.assertEqual(
            form.widgets['transition'].terms.terms.by_token.keys(),
            [])

        # only one selected element
        # doc1
        doc_uids = u"{0}".format(self.doc1.UID())
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('transition-batch-action')
        form.update()
        self.assertEqual(
            form.widgets['transition'].terms.terms.by_token.keys(),
            ['retract', 'reject'])
        # doc2
        doc_uids = u"{0}".format(self.doc2.UID())
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('transition-batch-action')
        form.update()
        self.assertEqual(
            form.widgets['transition'].terms.terms.by_token.keys(),
            ['publish', 'submit'])

    def test_transition_action_button_visibility(self):
        """Button 'Apply' is only shown if there are common transitions."""
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('transition-batch-action')
        # button is shown as there are common transitions
        form.update()
        self.assertTrue(form.widgets['transition'].terms.terms.by_token.keys())
        apply_button = form.buttons.get('apply')
        self.assertTrue(bool(apply_button.condition(form)))

        # change state of doc1, no common transition available
        api.content.transition(self.doc1, 'publish')
        form = self.eea_folder.restrictedTraverse('transition-batch-action')
        form.update()
        self.assertFalse(bool(apply_button.condition(form)))

    def test_delete_action(self):
        """Delete batch action."""
        login(self.portal.aq_parent, "admin")
        # make eea_folder not deletable
        self.eea_folder.manage_permission(DeleteObjects, [])
        self.assertFalse(_checkPermission(DeleteObjects, self.eea_folder))
        # set 'uids' in form, 2 deletable elements, one not deletable
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('delete-batch-action')
        form.update()
        self.assertTrue("This action will affect 2 element(s)." in form.render())
        # when some not deletable a specific description is displayed
        doc_uids = u"{0},{1},{2}".format(self.doc1.UID(), self.doc2.UID(), self.eea_folder.UID())
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('delete-batch-action')
        form.update()
        self.assertTrue("This action will only affect 2 element(s), "
                        "indeed you do not have the permission to delete 1 element(s)."
                        in form.render())

        # apply button title is changed using the form.apply_button_title
        self.assertEqual(form.actions['apply'].title, u'delete-batch-action-but')
        # apply, 2 elements are deleted
        form.handleApply(form, None)
        self.assertFalse('doc1' in self.portal.objectIds())
        self.assertFalse('doc2' in self.portal.objectIds())
        self.assertTrue('eea_folder' in self.portal.objectIds())

    def test_action_form_available(self):
        """Check available_permission and available_for_zope_admin."""
        api.user.create(email="test@test.org", username="new_user", password="secret")
        form = BaseBatchActionForm(self.portal, self.request)
        login(self.portal, "new_user")
        # available_permission
        self.assertFalse(form.available_permission)
        self.assertFalse(form.available_for_zope_admin)
        self.assertTrue(form.available())
        form.available_permission = ManagePortal
        self.assertFalse(form.available())
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(form.available())
        # available_for_zope_admin
        login(self.portal, "new_user")
        form.available_permission = ''
        form.available_for_zope_admin = True
        self.assertFalse(form.available())
        login(self.portal, TEST_USER_NAME)
        self.assertTrue(_checkPermission(ManagePortal, self.portal))
        self.assertFalse(form.available())
        login(self.portal.aq_parent, "admin")
        self.assertTrue(_checkPermission(ManagePortal, self.portal))
        self.assertTrue(form.available())

    def test_update_wf_role_mappings_action(self):
        """Update WF role mappings action."""
        # for now test user able to see and returned by catalog query
        self.assertTrue(_checkPermission(View, self.doc1))
        self.assertTrue(_checkPermission(View, self.doc2))
        catalog = self.portal.portal_catalog
        self.assertEqual(len(catalog(UID=[self.doc1.UID(), self.doc2.UID()])), 2)
        # do a change in Document workflow, make only "Manager" able to View
        wf = self.portal.portal_workflow.getWorkflowsFor(self.doc1)[0]
        wf.states.private.permission_roles[AccessContentsInformation] = ('Manager', )
        wf.states.private.permission_roles[View] = ('Manager', )

        # action only available to Zope admin
        # set 'uids' in form
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('update-wf-role-mappings-batch-action')
        self.assertRaises(Unauthorized, form)

        # do it as Zope admin
        login(self.portal.aq_parent, 'admin')
        form.update()
        self.assertTrue("This action will affect 2 element(s)." in form.render())
        # apply, 2 elements are updated
        form.handleApply(form, None)

        # make test user no more Manager, can not access the action and the documents
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, TEST_USER_NAME)
        self.assertFalse(_checkPermission(View, self.doc1))
        self.assertFalse(_checkPermission(View, self.doc2))
        self.assertEqual(len(catalog(UID=[self.doc1.UID(), self.doc2.UID()])), 0)

    def do_test_aruo_action(self, vocab_name=True):
        """Update 'custom_portal_type' attribute."""
        addOrUpdateIndexes(
            self.portal,
            indexInfos={'custom_portal_types': ('KeywordIndex', {}), })
        catalog = self.portal.portal_catalog
        self.doc1.custom_portal_types = ['testtype']
        self.doc1.reindexObject()
        self.assertTrue(catalog(custom_portal_types='testtype'))
        self.assertFalse(catalog(custom_portal_types='Document'))
        self.assertFalse(catalog(custom_portal_types='position'))
        doc_uids = self.doc1.UID()
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('testing-aruo-batch-action')
        if vocab_name:
            form._vocabulary = lambda: 'plone.app.vocabularies.PortalTypes'
        form.update()
        # "testtype" portal_type is at the end of portal_types,
        # if we add "Document" portal_type, order is respected
        self.request['form.widgets.action_choice'] = 'add'
        self.request['form.widgets.added_values'] = ['Document']
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ['Document', 'testtype'])
        self.assertTrue(catalog(custom_portal_types='testtype'))
        self.assertTrue(catalog(custom_portal_types='Document'))
        self.assertFalse(catalog(custom_portal_types='position'))
        # "position" portal_type will be added between existing values
        self.request['form.widgets.added_values'] = ['position']
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ['Document', 'position', 'testtype'])
        self.assertTrue(catalog(custom_portal_types='testtype'))
        self.assertTrue(catalog(custom_portal_types='Document'))
        self.assertTrue(catalog(custom_portal_types='position'))
        # remove "position"
        self.request['form.widgets.action_choice'] = 'remove'
        self.request['form.widgets.added_values'] = []
        self.request['form.widgets.removed_values'] = ['position']
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ['Document', 'testtype'])
        self.assertTrue(catalog(custom_portal_types='testtype'))
        self.assertTrue(catalog(custom_portal_types='Document'))
        self.assertFalse(catalog(custom_portal_types='position'))
        # field is required, it is not possible to remove every values
        # remove 'testtype'
        self.request['form.widgets.removed_values'] = ['testtype']
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ['Document'])
        # trying to remove 'Document' will do nothing
        self.request['form.widgets.removed_values'] = ['Document']
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ['Document'])
        # replace, only replaced if exists
        self.request['form.widgets.action_choice'] = 'replace'
        self.request['form.widgets.added_values'] = ['position']
        self.request['form.widgets.removed_values'] = ['testtype']
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ['Document'])
        # now replace a really selected value
        self.request['form.widgets.removed_values'] = ['Document']
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ['position'])

    def test_aruo_action_with_true_vocab(self):
        """Update 'custom_portal_type' attribute."""
        self.do_test_aruo_action(vocab_name=False)

    def test_aruo_action_with_vocab_name(self):
        """Update 'custom_portal_type' attribute."""
        self.do_test_aruo_action(vocab_name=True)
