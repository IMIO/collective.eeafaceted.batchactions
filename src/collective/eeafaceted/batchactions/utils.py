# -*- coding: utf-8 -*-
"""Batch actions views."""

from AccessControl import getSecurityManager
from collective.eeafaceted.batchactions import _
from imio.helpers.content import uuidsToCatalogBrains


cannot_modify_field_msg = _(u"You can't change this field on selected items. Modify your selection.")


def is_permitted(brains, perm='Modify portal content', perms=None):
    """
    Check all brains to verify permissions, by default 'Modify portal content'
    `perms` overrides `perm` if defined
    """
    if perms is None:
        perms = (perm,)
    ret = True
    sm = getSecurityManager()
    for brain in brains:
        obj = brain.getObject()
        if not all([sm.checkPermission(p, obj) for p in perms]):
            ret = False
            break
    return ret


def has_interface(brains, itf):
    """ Check all brains to verify a provided interface """
    ret = True
    for brain in brains:
        obj = brain.getObject()
        if not itf.providedBy(obj):
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


def brains_from_uids(uids, ordered=True):
    """ Returns a list of brains from a string (comma separated) or a list, containing uids """
    if not uids:
        return []

    uids = listify_uids(uids)
    brains = uuidsToCatalogBrains(uids, ordered=ordered)
    return brains


def active_labels(labeling):
    """
        For ftw.labels only.
        Returns 2 list of active labels on an adapted object : personal and global
    """
    p_act, g_act = [], []
    for label_id in labeling.storage:
        try:
            label = labeling.jar.get(label_id)
            if label['by_user']:
                if labeling.user_id() in labeling.storage[label_id]:
                    p_act.append(label_id)
            else:
                g_act.append(label_id)
        except KeyError:
            pass
    return p_act, g_act
