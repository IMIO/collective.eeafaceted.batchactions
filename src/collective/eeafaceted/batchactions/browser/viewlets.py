# -*- coding: utf-8 -*-

from collective.eeafaceted.batchactions.interfaces import IBatchActionsMarker
from operator import itemgetter
from plone.app.layout.viewlets import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.interface import Interface


class BatchActionsViewlet(ViewletBase):
    ''' '''

    index = ViewPageTemplateFile("templates/batch_actions_viewlet.pt")

    def available(self):
        """Global availability of the viewlet."""
        return True

    def _get_marker_interfaces(self):
        """By default views are registered for the IBatchActionsMarker
           interface, but in case it is needed to register different views,
           it is possible to use a more specific marker interface that inherits
           from IBatchActionsMarker."""
        ifaces = [IBatchActionsMarker]
        # check if context is marked with an interface
        # inheriting from IBatchActionsMarker
        for iface in self.context.__provides__:
            if IBatchActionsMarker in iface.__bases__:
                ifaces.append(iface)
        return ifaces

    def get_batch_actions(self):
        """We return every views that are registered for
           IBatchActionsMarker and sub interfaces."""
        # get the marker interfaces the views are registered for
        # as the viewlet is registered for IBatchActionsMarker, we will at least
        # get this interfaces in _get_marker_interfaces
        marker_interfaces = self._get_marker_interfaces()

        # get every views registered for the marker_interfaces
        gsm = getGlobalSiteManager()
        registered_actions = [
            a for a in gsm.registeredAdapters()
            if set(marker_interfaces).intersection(set(a.required)) and
            a.provided == Interface]
        # in case a view is registered several times for different interfaces,
        # we have the same name several times and we remove duplicates.
        # When getting the view, the ZCA will do the job
        registered_actions = set([action.name for action in registered_actions])
        # now check that action is available
        actions = []
        for registered_action in registered_actions:
            form = getMultiAdapter((self.context, self.request), name=registered_action)
            if form.available():
                actions.append({
                    'name': registered_action,
                    'button_with_icon': form.button_with_icon,
                    'overlay': form.overlay,
                    'weight': form.weight})
        actions.sort(key=itemgetter('weight'))
        return actions
