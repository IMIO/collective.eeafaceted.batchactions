# -*- coding: utf-8 -*-
"""Batch actions views."""

from AccessControl import getSecurityManager
from collective.eeafaceted.batchactions import _
from plone import api

cannot_modify_field_msg = _(u"You can't change this field on selected items. Modify your selection.")


def is_permitted(brains, perm='Modify portal content'):
    """ Check all brains to verify a permission, by default 'Modify portal content' """
    ret = True
    sm = getSecurityManager()
    for brain in brains:
        obj = brain.getObject()
        if not sm.checkPermission(perm, obj):
            ret = False
            break
    return ret


def filter_on_permission(brains, perm='Modify portal content'):
    """ Return only objects where current user has the permission """
    ret = []
    sm = getSecurityManager()
    for brain in brains:
        obj = brain.getObject()
        if sm.checkPermission(perm, obj):
            ret.append(obj)
    return ret


def listify_uids(uids):
    """ uids is received as a string separated by commas, turn it into a real list """
    if isinstance(uids, basestring):
        uids = uids.split(',')
    return uids


def brains_from_uids(uids):
    """ Returns a list of brains from a string (comma separated) or a list, containing uids """
    if not uids:
        return []

    catalog = api.portal.get_tool('portal_catalog')
    uids = listify_uids(uids)
    brains = catalog(UID=uids)
    return brains
