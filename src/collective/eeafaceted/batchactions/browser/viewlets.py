# -*- coding: utf-8 -*-

from collective.eeafaceted.batchactions.interfaces import IBatchActionsMarker
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getGlobalSiteManager
from zope.interface import directlyProvidedBy
from zope.interface import Interface


class BatchActions(ViewletBase):
    ''' '''

    index = ViewPageTemplateFile("templates/batch_actions_viewlet.pt")

    def available(self):
        """ """
        return True

    def _get_marker_interfaces(self):
        """By default views are registered for the IBatchActionsMarker
           interface, but in case it is needed to register different views,
           it is possible to use a more specific marker interface that inherits
           from IBatchActionsMarker."""
        ifaces = [IBatchActionsMarker]
        # directly provided
        if IBatchActionsMarker in directlyProvidedBy(self.context):
            return ifaces

        # check if context is marked with an interface
        # inheriting from IBatchActionsMarker
        for iface in self.context.__provides__:
            if IBatchActionsMarker in iface.__bases__:
                ifaces.append(iface)
        return ifaces

    def get_batch_action_names(self):
        """We return every views that are registered for
           IBatchActionsMarker and sub interfaces."""

        # get the marker interfaces the views are registered for
        marker_interfaces = self._get_marker_interfaces()
        if not marker_interfaces:
            return []

        # get every views registered for the marker_interfaces
        gsm = getGlobalSiteManager()
        registered_actions = [
            a for a in gsm.registeredAdapters()
            if set(marker_interfaces).intersection(set(a.required)) and
            a.provided == Interface]
        # in case a view is registered several times for different interfaces,
        # we have the same name several times and we remove duplicates.
        # When getting the view, the ZCA will do the job
        return set([action.name for action in registered_actions])