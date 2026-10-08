# -*- coding: utf-8 -*-

from collective.eeafaceted.batchactions.testing import LABELS_FUNCTIONAL
from collective.eeafaceted.batchactions.tests.base import BaseTestCase
from collective.eeafaceted.batchactions.utils import active_labels
from collective.eeafaceted.batchactions.utils import cannot_modify_field_msg
from collective.labels.interfaces import ILabeling
from collective.labels.interfaces import ILabelJar
from collective.labels.interfaces import ILabelRoot
from collective.labels.interfaces import ILabelSupport
from plone import api
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from zope.interface import alsoProvides


class TestLabels(BaseTestCase):

    layer = LABELS_FUNCTIONAL

    def setUp(self):
        """ """
        super(TestLabels, self).setUp()
        self.doc1 = api.content.create(self.portal, "Document", "doc1")
        self.doc2 = api.content.create(self.portal, "Document", "doc2")
        # defined some labels
        alsoProvides(self.portal, ILabelRoot)
        adapted = ILabelJar(self.portal)
        adapted.add("Pers1", "green", True)  # label_id = pers1
        adapted.add("Pers2", "green", True)  # label_id = pers2
        adapted.add("Pers3", "green", True)  # label_id = pers3
        adapted.add("Glob1", "red", False)  # label_id = glob1
        adapted.add("Glob2", "red", False)  # label_id = glob2
        adapted.add("Glob3", "red", False)  # label_id = glob3
        # can label created objects
        for obj in (self.doc1, self.doc2):
            alsoProvides(obj, ILabelSupport)
        self.lab_doc1 = ILabeling(self.doc1)
        self.lab_doc2 = ILabeling(self.doc2)
        login(self.portal, TEST_USER_NAME)

    def test_LabelsBatchActionForm_apply(self):
        # set 'uids' in form
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form["form.widgets.uids"] = doc_uids
        form = self.eea_folder.restrictedTraverse("labels-batch-action")
        form.update()
        # labels are found
        self.assertListEqual(
            sorted(form.widgets["added_values"].terms.terms.by_value),
            ["glob1", "glob2", "glob3", "pers1:", "pers2:", "pers3:"],
        )
        # no assigned label
        self.assertTupleEqual(active_labels(self.lab_doc1), ([], []))
        self.assertTupleEqual(active_labels(self.lab_doc2), ([], []))

        # test add action
        form.widgets.extract = lambda *a, **kw: (
            {"action_choice": "add", "added_values": ["pers1:", "glob1"]},
            [],
        )
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), (["pers1"], ["glob1"]))
        self.assertTupleEqual(active_labels(self.lab_doc2), (["pers1"], ["glob1"]))
        # add another pers label
        form.widgets.extract = lambda *a, **kw: (
            {"action_choice": "add", "added_values": ["pers2:"]},
            [],
        )
        form.handleApply(form, None)
        act_lab = active_labels(self.lab_doc1)
        self.assertSetEqual(set(act_lab[0]), set(["pers1", "pers2"]))
        self.assertSetEqual(set(act_lab[1]), set(["glob1"]))
        # add another glob label
        form.widgets.extract = lambda *a, **kw: (
            {"action_choice": "add", "added_values": ["pers2:", "glob1", "glob2"]},
            [],
        )
        form.handleApply(form, None)
        act_lab = active_labels(self.lab_doc1)
        self.assertSetEqual(set(act_lab[0]), set(["pers1", "pers2"]))
        self.assertSetEqual(set(act_lab[1]), set(["glob1", "glob2"]))

        # test remove action
        form.widgets.extract = lambda *a, **kw: (
            {"action_choice": "remove", "removed_values": ["pers1:", "glob1"]},
            [],
        )
        form.handleApply(form, None)
        act_lab = active_labels(self.lab_doc1)
        self.assertSetEqual(set(act_lab[0]), set(["pers2"]))
        self.assertSetEqual(set(act_lab[1]), set(["glob2"]))
        # remove all
        form.widgets.extract = lambda *a, **kw: (
            {
                "action_choice": "remove",
                "removed_values": ["pers1:", "pers2:", "glob1", "glob2"],
            },
            [],
        )
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), ([], []))

        # test replace action
        # in case of a 'replace', values are replaced only if it was actually selected on the element
        # so here as nothing selected anymore, nothing changed
        form.widgets.extract = lambda *a, **kw: (
            {
                "action_choice": "replace",
                "removed_values": ["pers1:", "glob1"],
                "added_values": ["pers2:", "pers3:", "glob2", "glob3"],
            },
            [],
        )
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), ([], []))

        # now add a value and replace it
        # add
        form.widgets.extract = lambda *a, **kw: (
            {"action_choice": "add", "added_values": ["pers1:", "glob1"]},
            [],
        )
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), (["pers1"], ["glob1"]))
        # replace
        form.widgets.extract = lambda *a, **kw: (
            {
                "action_choice": "replace",
                "removed_values": ["pers1:", "glob1"],
                "added_values": ["pers2:", "glob2"],
            },
            [],
        )
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), (["pers2"], ["glob2"]))

        # test overwrite action
        form.widgets.extract = lambda *a, **kw: (
            {"action_choice": "overwrite", "added_values": ["pers1:", "glob3"]},
            [],
        )
        form.handleApply(form, None)
        act_lab = active_labels(self.lab_doc1)
        self.assertSetEqual(set(act_lab[0]), set(["pers1"]))
        self.assertSetEqual(set(act_lab[1]), set(["glob3"]))

    def test_LabelsBatchActionForm_get_labels_vocabulary(self):
        """Global labels are only proposed (and changed) with "collective.labels: Change Labels" on every element,
        personal labels are marked with (*)."""
        self.request.form["form.widgets.uids"] = u"{0},{1}".format(
            self.doc1.UID(), self.doc2.UID()
        )
        form = self.eea_folder.restrictedTraverse("labels-batch-action")
        form.update()
        self.assertTrue(form.can_change_labels)
        self.assertEqual(
            sorted(
                (term.value, term.token, term.title)
                for term in form.widgets["added_values"].terms.terms
            ),
            [
                ("glob1", "glob1", u"Glob1"),
                ("glob2", "glob2", u"Glob2"),
                ("glob3", "glob3", u"Glob3"),
                ("pers1:", "pers1", u"Pers1 (*)"),
                ("pers2:", "pers2", u"Pers2 (*)"),
                ("pers3:", "pers3", u"Pers3 (*)"),
            ],
        )
        self.assertEqual(form.p_labels, set(["pers1", "pers2", "pers3"]))
        self.assertEqual(sorted(form.g_labels), ["glob1", "glob2", "glob3"])
        # without the permission on one element (Reader on doc2), only personal labels
        api.user.create(
            email="test@test.org", username="new_user", password="secret123"
        )
        api.user.grant_roles(username="new_user", obj=self.eea_folder, roles=["Reader"])
        api.user.grant_roles(username="new_user", obj=self.doc1, roles=["Editor"])
        api.user.grant_roles(username="new_user", obj=self.doc2, roles=["Reader"])
        for obj in (self.eea_folder, self.doc1, self.doc2):
            obj.reindexObjectSecurity()
        login(self.portal, "new_user")
        form = self.eea_folder.restrictedTraverse("labels-batch-action")
        form.update()
        self.assertEqual(len(form.brains), 2)
        self.assertFalse(form.can_change_labels)
        self.assertEqual(
            sorted(form.widgets["added_values"].terms.terms.by_value),
            ["pers1:", "pers2:", "pers3:"],
        )
        # a global label is not applied
        form.widgets.extract = lambda *a, **kw: (
            {"action_choice": "add", "added_values": ["pers1:", "glob1"]},
            [],
        )
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), (["pers1"], []))
        self.assertTupleEqual(active_labels(self.lab_doc2), (["pers1"], []))

    def test_LabelsBatchActionForm_may_apply(self):
        """Can not be applied when an element does not support labels or no label is defined."""
        doc3 = api.content.create(self.portal, "Document", "doc3")
        self.request.form["form.widgets.uids"] = u"{0},{1}".format(
            self.doc1.UID(), doc3.UID()
        )
        form = self.eea_folder.restrictedTraverse("labels-batch-action")
        form.update()
        self.assertFalse(form.do_apply)
        self.assertEqual(
            form.widgets["action_choice"].field.description, cannot_modify_field_msg
        )
        self.assertNotIn("added_values", form.widgets)
        self.assertNotIn("apply", form.actions)
        # labelable elements
        self.request.form["form.widgets.uids"] = u"{0},{1}".format(
            self.doc1.UID(), self.doc2.UID()
        )
        form = self.eea_folder.restrictedTraverse("labels-batch-action")
        form.update()
        self.assertTrue(form.do_apply)
        self.assertIn("added_values", form.widgets)
        # no label defined
        jar = ILabelJar(self.portal)
        for label in jar.list():
            jar.remove(label["label_id"])
        form = self.eea_folder.restrictedTraverse("labels-batch-action")
        form.update()
        self.assertFalse(form.do_apply)
        self.assertNotIn("added_values", form.widgets)
