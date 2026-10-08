# -*- coding: utf-8 -*-

from AccessControl import Unauthorized
from collective.eeafaceted.batchactions.browser.views import BaseBatchActionForm
from collective.eeafaceted.batchactions.tests.base import BaseTestCase
from collective.eeafaceted.batchactions.utils import cannot_modify_field_msg
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
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.lifecycleevent.interfaces import IObjectModifiedEvent


class TestActions(BaseTestCase):
    def _tokens(self, form):
        """Tokens of the transition vocabulary, sorted on the transition titles
        ('Member submits...' < 'Reviewer publishes...')."""
        return [term.token for term in form.widgets["transition"].terms.terms]

    def setUp(self):
        """ """
        super(TestActions, self).setUp()
        self.doc1 = api.content.create(
            type="Document", id="doc1", title="Document 1", container=self.portal
        )
        self.doc2 = api.content.create(
            type="Document", id="doc2", title="Document 2", container=self.portal
        )

    def test_transition_action_apply(self):
        """Working behavior, we have several documents with same transition available."""
        # set 'uids' in form
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("transition-batch-action")
        # common transitions are shown, here it is the case as docs are in same state
        form.update()
        self.assertEqual(self._tokens(form), ["submit", "publish"])
        form.request["form.widgets.transition"] = "publish"
        form.request["form.widgets.comment"] = u"Published in batch"
        extracted_data, errors = form.extractData()
        self.assertEqual(
            extracted_data,
            {
                "comment": u"Published in batch",
                "transition": "publish",
                "referer": None,
                "uids": doc_uids,
            },
            (),
        )

        # for now both docs are 'private'
        self.assertEqual(
            [api.content.get_state(self.doc1), api.content.get_state(self.doc2)],
            ["private", "private"],
        )
        form.handleApply(form, None)
        self.assertEqual(
            [api.content.get_state(self.doc1), api.content.get_state(self.doc2)],
            ["published", "published"],
        )
        # the comment is stored in the workflow history
        wf_tool = self.portal.portal_workflow
        for doc in (self.doc1, self.doc2):
            last_event = wf_tool.getHistoryOf("simple_publication_workflow", doc)[-1]
            self.assertEqual(
                (last_event["action"], last_event["comments"]),
                ("publish", u"Published in batch"),
            )

    def test_transition_action_cancel(self):
        """When cancelled, nothing is done and user is redirected to referer."""
        form = getMultiAdapter(
            (self.eea_folder, self.request), name="transition-batch-action"
        )
        self.request["HTTP_REFERER"] = self.portal.absolute_url()
        self.request.RESPONSE.status = 200
        self.assertNotEqual(
            self.request.RESPONSE.getHeader("location"), self.request["HTTP_REFERER"]
        )
        form.handleCancel(form, None)
        self.assertEqual(self.request.RESPONSE.status, 302)
        self.assertEqual(
            self.request.RESPONSE.getHeader("location"), self.request["HTTP_REFERER"]
        )

    def test_transition_action_uids_can_be_defined_on_request_or_form(self):
        """'uids' used by the form are retrieved no matter it is defined on
        self.request or self.request.form."""
        # set 'uids' in self.request.form
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("transition-batch-action")
        # common transitions are shown, here it is the case as docs are in same state
        form.update()
        extracted_data, errors = form.extractData()
        self.assertEqual(extracted_data["uids"], doc_uids)
        del self.request.form["form.widgets.uids"]

        # set 'uids' in self.request
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request["uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("transition-batch-action")
        # common transitions are shown, here it is the case as docs are in same state
        form.update()
        extracted_data, errors = form.extractData()
        self.assertEqual(extracted_data["uids"], doc_uids)

    def test_transition_action_only_list_common_transitions(self):
        """Only work if there are common transitions for selected elements."""
        # set 'uids' in form
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("transition-batch-action")
        # common transitions are shown, here it is the case as docs are in same state
        form.update()
        self.assertEqual(self._tokens(form), ["submit", "publish"])

        # change state of doc1, no common transition available
        api.content.transition(self.doc1, "publish")
        form = self.eea_folder.restrictedTraverse("transition-batch-action")
        form.update()
        self.assertEqual(self._tokens(form), [])

        # only one selected element
        # doc1
        doc_uids = u"{0}".format(self.doc1.UID())
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("transition-batch-action")
        form.update()
        self.assertEqual(self._tokens(form), ["retract", "reject"])
        # doc2
        doc_uids = u"{0}".format(self.doc2.UID())
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("transition-batch-action")
        form.update()
        self.assertEqual(self._tokens(form), ["submit", "publish"])

    def test_transition_action_button_visibility(self):
        """Button 'Apply' is only shown if there are common transitions."""
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("transition-batch-action")
        # button is shown as there are common transitions
        form.update()
        self.assertTrue(self._tokens(form))
        apply_button = form.buttons.get("apply")
        self.assertTrue(bool(apply_button.condition(form)))

        # change state of doc1, no common transition available
        api.content.transition(self.doc1, "publish")
        form = self.eea_folder.restrictedTraverse("transition-batch-action")
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
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("delete-batch-action")
        form.update()
        self.assertTrue("This action will affect 2 element(s)." in form.render())
        # when some not deletable a specific description is displayed
        doc_uids = u"{0},{1},{2}".format(
            self.doc1.UID(), self.doc2.UID(), self.eea_folder.UID()
        )
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("delete-batch-action")
        form.update()
        self.assertTrue(
            "This action will only affect 2 element(s), "
            "indeed you do not have the permission to delete 1 element(s)."
            in form.render()
        )

        # apply button title is changed using the form.apply_button_title
        self.assertEqual(form.actions["apply"].title, u"delete-batch-action-but")
        # apply, 2 elements are deleted
        form.handleApply(form, None)
        self.assertFalse("doc1" in self.portal.objectIds())
        self.assertFalse("doc2" in self.portal.objectIds())
        self.assertTrue("eea_folder" in self.portal.objectIds())

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
        form.available_permission = ""
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
        wf.states.private.permission_roles[AccessContentsInformation] = ("Manager",)
        wf.states.private.permission_roles[View] = ("Manager",)

        # action only available to Zope admin
        # set 'uids' in form
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse(
            "update-wf-role-mappings-batch-action"
        )
        self.assertRaises(Unauthorized, form)

        # do it as Zope admin
        login(self.portal.aq_parent, "admin")
        form.update()
        self.assertTrue("This action will affect 2 element(s)." in form.render())
        # apply, 2 elements are updated
        form.handleApply(form, None)

        # make test user no more Manager, can not access the action and the documents
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, TEST_USER_NAME)
        self.assertFalse(_checkPermission(View, self.doc1))
        self.assertFalse(_checkPermission(View, self.doc2))
        self.assertEqual(len(catalog(UID=[self.doc1.UID(), self.doc2.UID()])), 0)

    def do_test_aruo_action(self, vocab_name=True):
        """Update 'custom_portal_type' attribute."""
        addOrUpdateIndexes(
            self.portal,
            indexInfos={
                "custom_portal_types": ("KeywordIndex", {}),
            },
        )
        catalog = self.portal.portal_catalog
        self.doc1.custom_portal_types = ["testtype"]
        self.doc1.reindexObject()
        self.assertTrue(catalog(custom_portal_types="testtype"))
        self.assertFalse(catalog(custom_portal_types="Document"))
        self.assertFalse(catalog(custom_portal_types="Folder"))
        # objects are notified as modified (call_modified_event)
        modified_uids = []

        def handler(event):
            modified_uids.append(event.object.UID())

        gsm = getGlobalSiteManager()
        gsm.registerHandler(handler, (IObjectModifiedEvent,))
        self.addCleanup(gsm.unregisterHandler, handler, (IObjectModifiedEvent,))
        doc_uids = self.doc1.UID()
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("testing-aruo-batch-action")
        if vocab_name:
            form._vocabulary = lambda: "plone.app.vocabularies.PortalTypes"
        form.update()
        # values are stored in vocabulary order (portal types sorted on title:
        # "Folder", "Page" (Document), "Test type" (testtype))
        self.request["form.widgets.action_choice"] = "add"
        self.request["form.widgets.added_values"] = ["Document"]
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ["Document", "testtype"])
        self.assertEqual(modified_uids, [self.doc1.UID()])
        self.assertTrue(catalog(custom_portal_types="testtype"))
        self.assertTrue(catalog(custom_portal_types="Document"))
        self.assertFalse(catalog(custom_portal_types="Folder"))
        # "Folder" portal_type will be added before existing values
        self.request["form.widgets.added_values"] = ["Folder"]
        form.handleApply(form, None)
        self.assertEqual(
            self.doc1.custom_portal_types, ["Folder", "Document", "testtype"]
        )
        self.assertTrue(catalog(custom_portal_types="testtype"))
        self.assertTrue(catalog(custom_portal_types="Document"))
        self.assertTrue(catalog(custom_portal_types="Folder"))
        # remove "Folder"
        self.request["form.widgets.action_choice"] = "remove"
        self.request["form.widgets.added_values"] = []
        self.request["form.widgets.removed_values"] = ["Folder"]
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ["Document", "testtype"])
        self.assertTrue(catalog(custom_portal_types="testtype"))
        self.assertTrue(catalog(custom_portal_types="Document"))
        self.assertFalse(catalog(custom_portal_types="Folder"))
        # field is required, it is not possible to remove every values
        # remove 'testtype'
        self.request["form.widgets.removed_values"] = ["testtype"]
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ["Document"])
        self.assertEqual(len(modified_uids), 4)
        # trying to remove 'Document' will do nothing
        self.request["form.widgets.removed_values"] = ["Document"]
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ["Document"])
        self.assertEqual(len(modified_uids), 4)
        # replace, only replaced if exists
        self.request["form.widgets.action_choice"] = "replace"
        self.request["form.widgets.added_values"] = ["Folder"]
        self.request["form.widgets.removed_values"] = ["testtype"]
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ["Document"])
        # now replace a really selected value
        self.request["form.widgets.removed_values"] = ["Document"]
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ["Folder"])
        # overwrite, whatever the stored values, in vocabulary order
        self.request["form.widgets.action_choice"] = "overwrite"
        self.request["form.widgets.added_values"] = ["testtype", "Document"]
        self.request["form.widgets.removed_values"] = []
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ["Document", "testtype"])
        self.assertEqual(len(modified_uids), 6)
        # no modified event when call_modified_event is False
        form.call_modified_event = False
        self.request["form.widgets.added_values"] = ["Folder"]
        form.handleApply(form, None)
        self.assertEqual(self.doc1.custom_portal_types, ["Folder"])
        self.assertEqual(len(modified_uids), 6)

    def test_aruo_action_with_true_vocab(self):
        """Update 'custom_portal_type' attribute."""
        self.do_test_aruo_action(vocab_name=False)

    def test_aruo_action_with_vocab_name(self):
        """Update 'custom_portal_type' attribute."""
        self.do_test_aruo_action(vocab_name=True)

    def test_update(self):
        """The referer encoded by batch_actions.js is decoded ('@' -> '&', '!' -> '#')
        unless already in the form, buttons are ordered apply/cancel."""
        # batch_actions.js POSTs uids and referer (a GET request is ignored by the widgets)
        self.request.environ["REQUEST_METHOD"] = "POST"
        self.request.form["uids"] = self.doc1.UID()
        self.request.form[
            "referer"
        ] = "http://nohost/plone/eea_folder?b_start=20@sort_on=sortable_title!c3=20"
        form = getMultiAdapter(
            (self.eea_folder, self.request), name="transition-batch-action"
        )
        form.update()
        self.assertEqual(
            self.request.form["form.widgets.referer"],
            u"http://nohost/plone/eea_folder?b_start=20&sort_on=sortable_title#c3=20",
        )
        self.assertEqual(self.request.form["form.widgets.uids"], self.doc1.UID())
        # hidden in the rendered form, posted with the apply button
        self.assertEqual(
            form.widgets["referer"].value,
            u"http://nohost/plone/eea_folder?b_start=20&sort_on=sortable_title#c3=20",
        )
        self.assertEqual(form.widgets["uids"].value, self.doc1.UID())
        self.assertEqual(list(form.actions.keys()), ["apply", "cancel"])
        # submitted form: the referer widget value is kept as is
        # (as processInputs did with the first form, the form values are mirrored in request.other)
        self.request.form[
            "form.widgets.referer"
        ] = u"http://nohost/plone/eea_folder?a=1@b=2"
        self.request.set(
            "form.widgets.referer", u"http://nohost/plone/eea_folder?a=1@b=2"
        )
        form = getMultiAdapter(
            (self.eea_folder, self.request), name="transition-batch-action"
        )
        form.update()
        self.assertEqual(
            form.widgets["referer"].value, u"http://nohost/plone/eea_folder?a=1@b=2"
        )

    def test_handleApply(self):
        """Without overlay, redirect to the referer. In the overlay (ajax_load), status 204 and
        nothing returned, unless _apply returned something."""
        # BaseTestCase.setUp left the 302 of the faceted enable()
        self.request.response.setStatus(200)
        self.request.form["form.widgets.uids"] = self.doc1.UID()
        self.request.form[
            "referer"
        ] = "http://nohost/plone/eea_folder?b_start=20@sort_on=sortable_title!c3=20"
        self.request.form["form.widgets.transition"] = "publish"
        form = getMultiAdapter(
            (self.eea_folder, self.request), name="transition-batch-action"
        )
        form.update()
        self.assertIsNone(form.handleApply(form, None))
        self.assertEqual(api.content.get_state(self.doc1), "published")
        self.assertEqual(self.request.response.getStatus(), 302)
        self.assertEqual(
            self.request.response.getHeader("location"),
            "http://nohost/plone/eea_folder?b_start=20&sort_on=sortable_title#c3=20",
        )
        # in the overlay
        self.request.response.setStatus(200)
        self.request.form["ajax_load"] = "1"
        self.request["form.widgets.transition"] = "retract"
        form = getMultiAdapter(
            (self.eea_folder, self.request), name="transition-batch-action"
        )
        form.update()
        self.assertEqual(form.handleApply(form, None), "")
        self.assertEqual(api.content.get_state(self.doc1), "private")
        self.assertEqual(self.request.response.getStatus(), 204)
        # the ARUO forms return the modified objects
        addOrUpdateIndexes(
            self.portal,
            indexInfos={
                "custom_portal_types": ("KeywordIndex", {}),
            },
        )
        self.doc1.custom_portal_types = []
        self.request.response.setStatus(200)
        self.request["form.widgets.action_choice"] = "add"
        self.request["form.widgets.added_values"] = ["Document"]
        form = getMultiAdapter(
            (self.eea_folder, self.request), name="testing-aruo-batch-action"
        )
        form.update()
        self.assertEqual(
            [obj.UID() for obj in form.handleApply(form, None)], [self.doc1.UID()]
        )
        self.assertEqual(self.request.response.getStatus(), 200)

    def test___call__(self):
        """The form is rendered, but nothing after a redirect or a 204 (overlay)."""
        # BaseTestCase.setUp left the 302 of the faceted enable()
        self.request.response.setStatus(200)
        self.request.form["form.widgets.uids"] = self.doc1.UID()
        form = getMultiAdapter(
            (self.eea_folder, self.request), name="transition-batch-action"
        )
        self.assertIn('id="form-buttons-apply"', form())
        self.request.form["form.widgets.transition"] = "publish"
        self.request.form["form.buttons.apply"] = "Apply"
        form = getMultiAdapter(
            (self.eea_folder, self.request), name="transition-batch-action"
        )
        self.assertEqual(form(), u"")
        self.assertEqual(self.request.response.getStatus(), 302)
        self.assertEqual(api.content.get_state(self.doc1), "published")
        # in the overlay
        self.request.response.setStatus(200)
        self.request.form["ajax_load"] = "1"
        self.request["form.widgets.transition"] = "retract"
        form = getMultiAdapter(
            (self.eea_folder, self.request), name="transition-batch-action"
        )
        self.assertEqual(form(), u"")
        self.assertEqual(self.request.response.getStatus(), 204)
        self.assertEqual(api.content.get_state(self.doc1), "private")

    def test_aruo_action_update(self):
        """Without "Modify portal content" on every element, the action can not be applied."""
        api.content.transition(self.eea_folder, "publish")
        api.content.transition(self.doc1, "publish")
        api.user.create(
            email="test@test.org", username="new_user", password="secret123"
        )
        self.request.form["form.widgets.uids"] = self.doc1.UID()
        form = self.eea_folder.restrictedTraverse("testing-aruo-batch-action")
        form.update()
        self.assertTrue(form.do_apply)
        self.assertEqual(form.widgets["action_choice"].field.description, u"")
        self.assertEqual(
            sorted(form.widgets.keys()),
            ["action_choice", "added_values", "referer", "removed_values", "uids"],
        )
        self.assertIn("apply", form.actions)
        # a Member can view doc1 but not modify it
        login(self.portal, "new_user")
        form = self.eea_folder.restrictedTraverse("testing-aruo-batch-action")
        form.update()
        self.assertFalse(form.do_apply)
        self.assertEqual(
            form.widgets["action_choice"].field.description, cannot_modify_field_msg
        )
        self.assertEqual(
            sorted(form.widgets.keys()), ["action_choice", "referer", "uids"]
        )
        self.assertNotIn("apply", form.actions)
        self.assertRaises(Unauthorized, form.handleApply, form, None)

    def test_aruo_action_description(self):
        """Number of elements, then the "required" and "replace" warnings."""
        self.request.form["form.widgets.uids"] = u"{0},{1}".format(
            self.doc1.UID(), self.doc2.UID()
        )
        form = self.eea_folder.restrictedTraverse("testing-aruo-batch-action")
        form.update()
        # Plone 4 known issue: the en msgstr of both warnings are empty, the msgids are shown
        self.assertEqual(
            form.description,
            u"This action will affect 2 element(s).field_can_not_be_empty_warningaruo_action_replace_warning",
        )
        form.required = False
        self.assertEqual(
            form.description,
            u"This action will affect 2 element(s).aruo_action_replace_warning",
        )
