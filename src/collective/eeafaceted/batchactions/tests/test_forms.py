# -*- coding: utf-8 -*-

from zope.component import getMultiAdapter
from collective.eeafaceted.batchactions.tests.base import BaseTestCase
from plone import api


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
