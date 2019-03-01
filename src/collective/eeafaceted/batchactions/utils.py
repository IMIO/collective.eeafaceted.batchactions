# -*- coding: utf-8 -*-
"""Batch actions views."""

from AccessControl import getSecurityManager
from collective.eeafaceted.batchactions import _

cannot_modify_field_msg = _(u"You can't change this field on selected items. Modify your selection.")


def is_not_permitted(brains, perm='Modify portal content'):
    """ Check all brains to verify a permission, by default 'Modify portal content' """
    problem = False
    sm = getSecurityManager()
    for brain in brains:
        obj = brain.getObject()
        if not sm.checkPermission(perm, obj):
            problem = True
            break
    return problem


def filter_on_permission(brains, perm='Modify portal content'):
    """ Return only objects where current user has the permission """
    ret = []
    sm = getSecurityManager()
    for brain in brains:
        obj = brain.getObject()
        if sm.checkPermission(perm, obj):
            ret.append(obj)
    return ret
