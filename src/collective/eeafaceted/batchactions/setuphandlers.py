# -*- coding: utf-8 -*-
from plone.base.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Hide the uninstall profile from the site creation and add-ons screens."""
        return ["collective.eeafaceted.batchactions:uninstall"]


def isNotCurrentProfile(context):
    return context.readDataFile("collectiveeeafacetedbatchactions_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return
