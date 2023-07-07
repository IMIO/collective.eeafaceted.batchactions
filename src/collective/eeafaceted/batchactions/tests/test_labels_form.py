# -*- coding: utf-8 -*-

from collective.eeafaceted.batchactions.tests.base import BaseTestCase
from collective.eeafaceted.batchactions.utils import active_labels
from ftw.labels.interfaces import ILabeling
from ftw.labels.interfaces import ILabelJar
from ftw.labels.interfaces import ILabelRoot
from ftw.labels.interfaces import ILabelSupport
from plone import api
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from zope.interface import alsoProvides


class TestLabels(BaseTestCase):

    def setUp(self):
        """ """
        super(TestLabels, self).setUp()
        self.doc1 = api.content.create(self.portal, 'Document', 'doc1')
        self.doc2 = api.content.create(self.portal, 'Document', 'doc2')
        # defined some labels
        alsoProvides(self.portal, ILabelRoot)
        adapted = ILabelJar(self.portal)
        adapted.add('Pers1', 'green', True)  # label_id = pers1
        adapted.add('Pers2', 'green', True)  # label_id = pers2
        adapted.add('Pers3', 'green', True)  # label_id = pers3
        adapted.add('Glob1', 'red', False)  # label_id = glob1
        adapted.add('Glob2', 'red', False)  # label_id = glob2
        adapted.add('Glob3', 'red', False)  # label_id = glob3
        # can label created objects
        for obj in (self.doc1, self.doc2):
            alsoProvides(obj, ILabelSupport)
        self.lab_doc1 = ILabeling(self.doc1)
        self.lab_doc2 = ILabeling(self.doc2)
        login(self.portal, TEST_USER_NAME)

    def test_LabelsBatchActionForm_apply(self):
        # set 'uids' in form
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        self.request.form['form.widgets.uids'] = doc_uids
        form = self.eea_folder.restrictedTraverse('labels-batch-action')
        form.update()
        # labels are found
        self.assertListEqual(
            form.widgets['added_values'].terms.terms.by_value.keys(),
            ['pers3:', 'pers2:', 'pers1:', 'glob3', 'glob2', 'glob1'])
        # no assigned label
        self.assertTupleEqual(active_labels(self.lab_doc1), ([], []))
        self.assertTupleEqual(active_labels(self.lab_doc2), ([], []))

        # test add action
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'add',
                                                  'added_values': ['pers1:', 'glob1']}, [])
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), (['pers1'], ['glob1']))
        self.assertTupleEqual(active_labels(self.lab_doc2), (['pers1'], ['glob1']))
        # add another pers label
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'add',
                                                  'added_values': ['pers2:']}, [])
        form.handleApply(form, None)
        act_lab = active_labels(self.lab_doc1)
        self.assertSetEqual(set(act_lab[0]), set(['pers1', 'pers2']))
        self.assertSetEqual(set(act_lab[1]), set(['glob1']))
        # add another glob label
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'add',
                                                  'added_values': ['pers2:', 'glob1', 'glob2']}, [])
        form.handleApply(form, None)
        act_lab = active_labels(self.lab_doc1)
        self.assertSetEqual(set(act_lab[0]), set(['pers1', 'pers2']))
        self.assertSetEqual(set(act_lab[1]), set(['glob1', 'glob2']))

        # test remove action
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'remove',
                                                  'removed_values': ['pers1:', 'glob1']}, [])
        form.handleApply(form, None)
        act_lab = active_labels(self.lab_doc1)
        self.assertSetEqual(set(act_lab[0]), set(['pers2']))
        self.assertSetEqual(set(act_lab[1]), set(['glob2']))
        # remove all
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'remove',
                                                  'removed_values': ['pers1:', 'pers2:', 'glob1', 'glob2']}, [])
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), ([], []))

        # test replace action
        # in case of a 'replace', values are replaced only if it was actually selected on the element
        # so here as nothing selected anymore, nothing changed
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'replace',
                                                  'removed_values': ['pers1:', 'glob1'],
                                                  'added_values': ['pers2:', 'pers3:', 'glob2', 'glob3']}, [])
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), ([], []))

        # now add a value and replace it
        # add
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'add',
                                                  'added_values': ['pers1:', 'glob1']}, [])
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), (['pers1'], ['glob1']))
        # replace
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'replace',
                                                  'removed_values': ['pers1:', 'glob1'],
                                                  'added_values': ['pers2:', 'glob2']}, [])
        form.handleApply(form, None)
        self.assertTupleEqual(active_labels(self.lab_doc1), (['pers2'], ['glob2']))

        # test overwrite action
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'overwrite',
                                                  'added_values': ['pers1:', 'glob3']}, [])
        form.handleApply(form, None)
        act_lab = active_labels(self.lab_doc1)
        self.assertSetEqual(set(act_lab[0]), set(['pers1']))
        self.assertSetEqual(set(act_lab[1]), set(['glob3']))
