# -*- coding: utf-8 -*-

from collective.eeafaceted.batchactions.tests.base import BaseTestCase
from collective.eeafaceted.batchactions.utils import brains_from_uids
from collective.eeafaceted.batchactions.utils import filter_on_permission
from collective.eeafaceted.batchactions.utils import is_permitted
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME


class TestUtils(BaseTestCase):

    def setUp(self):
        """ """
        super(TestUtils, self).setUp()
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
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Member'])

    def test_filter_on_permission(self):
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        brains = brains_from_uids(doc_uids)
        self.assertEquals(len(filter_on_permission(brains)), 2)
        self.assertEquals(len(filter_on_permission(brains, 'Review comments')), 0)
        setRoles(self.portal, TEST_USER_ID, ['Member', 'Reviewer'])
        self.assertEquals(len(filter_on_permission(brains, 'Review comments')), 2)

    def test_is_permitted(self):
        doc_uids = u"{0},{1}".format(self.doc1.UID(), self.doc2.UID())
        brains = brains_from_uids(doc_uids)
        self.assertTrue(is_permitted(brains))
        self.assertFalse(is_permitted(brains, 'Review comments'))

    def test_brains_from_uids(self):
        self.assertEqual(len(brains_from_uids('')), 0)
        self.assertEqual(len(brains_from_uids('{},{}'.format(self.doc1.UID(), self.doc2.UID()))), 2)
        self.assertEqual(len(brains_from_uids([self.doc1.UID(), self.doc2.UID()])), 2)
