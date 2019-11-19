# -*- coding: utf-8 -*-

from collective.eeafaceted.batchactions.tests.base import BaseTestCase
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class TestContactForm(BaseTestCase):

    def setUp(self):
        """ """
        super(TestContactForm, self).setUp()
        self.typ1 = api.content.create(self.eea_folder, 'testtype', 'typ1')
        self.typ2 = api.content.create(self.eea_folder, 'testtype', 'typ2')
        org1 = self.portal['mydirectory']['armeedeterre']
        org2 = org1['corpsa']
        org3 = org1['corpsb']
        self.intids = getUtility(IIntIds)
        self.orgs = [org1, org2, org3]
        self.rels = [RelationValue(self.intids.getId(org1)), RelationValue(self.intids.getId(org2)),
                     RelationValue(self.intids.getId(org3))]
        # set 'uids' in form
        typ_uids = u"{0},{1}".format(self.typ1.UID(), self.typ2.UID())
        self.request.form['form.widgets.uids'] = typ_uids

    def to_objs(self, rels):
        return sorted([self.intids.getObject(rel.to_id) for rel in rels or []], key=lambda x: self.orgs.index(x))

    def test_ContactBatchActionForm_available(self):
        login(self.portal, TEST_USER_NAME)
        form = self.eea_folder.restrictedTraverse('contact-batch-action')
        form.update()
        self.assertIn('Manager', api.user.get_roles())
        self.assertTrue(form.available())
        setRoles(self.portal, TEST_USER_ID, [])
        self.assertNotIn('Manager', api.user.get_roles())
        self.assertFalse(form.available())

    def test_ContactBatchActionForm_apply(self):
        form = self.eea_folder.restrictedTraverse('contact-batch-action')
        form.update()
        # test add action on None attributes
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'add',
                                                  'added_values': self.orgs[0:1]}, [])
        form.handleApply(form, None)
        self.assertEqual(self.to_objs(self.typ1.related_organizations), self.orgs[0:1])
        self.assertEqual(self.to_objs(self.typ2.related_organizations), self.orgs[0:1])
        # set values
        self.typ1.related_organizations = self.rels[0:2]
        self.typ2.related_organizations = self.rels[1:3]
        # test add action
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'add',
                                                  'added_values': self.orgs[0:1]}, [])
        form.handleApply(form, None)
        self.assertEqual(self.to_objs(self.typ1.related_organizations), self.orgs[0:2])
        self.assertEqual(self.to_objs(self.typ2.related_organizations), self.orgs)
        # test remove action
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'remove',
                                                  'removed_values': self.orgs[0:2]}, [])
        form.handleApply(form, None)
        self.assertEqual(self.to_objs(self.typ1.related_organizations), [])
        self.assertEqual(self.to_objs(self.typ2.related_organizations), self.orgs[2:3])
        # test replace action
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'replace',
                                                  'removed_values': self.orgs[1:3],
                                                  'added_values': self.orgs[0:2]}, [])
        form.handleApply(form, None)
        self.assertEqual(self.to_objs(self.typ1.related_organizations), self.orgs[0:2])
        self.assertEqual(self.to_objs(self.typ2.related_organizations), self.orgs[0:2])
        # test overwrite action
        form.widgets.extract = lambda *a, **kw: ({'action_choice': 'overwrite',
                                                  'added_values': self.orgs[1:3]}, [])
        form.handleApply(form, None)
        self.assertEqual(self.to_objs(self.typ1.related_organizations), self.orgs[1:3])
        self.assertEqual(self.to_objs(self.typ2.related_organizations), self.orgs[1:3])
