# -*- coding: utf-8 -*-
from zope.interface import Interface


class IBatchActionsMarker(Interface):
    """Marker interface for batch actions context."""


class IBatchActionSpecificMarker(IBatchActionsMarker):
    """A marker that is more specific thatn IBatchActionsMarker."""
