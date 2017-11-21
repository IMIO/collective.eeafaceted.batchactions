# -*- coding: utf-8 -*-

import unittest
from collective.eeafaceted.batchactions import testing
from collective.eeafaceted.batchactions.interfaces import IBatchActionsMarker
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from plone import api
from zope.interface import alsoProvides


class BaseTestCase(unittest.TestCase):

    layer = testing.FUNCTIONAL

    def setUp(self):
        """ """
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        # create a folder and enable faceted navigation on it
        eea_folder = api.content.create(
            type='Folder',
            id='eea_folder',
            title='EEA Folder',
            container=self.portal
        )
        alsoProvides(eea_folder, IBatchActionsMarker)
        eea_folder.reindexObject()
        eea_folder.restrictedTraverse('@@faceted_subtyper').enable()
        IFacetedLayout(eea_folder).update_layout('faceted-table-items')
        self.eea_folder = eea_folder
