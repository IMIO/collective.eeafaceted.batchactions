# -*- coding: utf-8 -*-
"""Batch actions views."""


from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone import api
from plone.supermodel import model
from z3c.form.form import EditForm
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.interfaces import HIDDEN_MODE

from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFPlone.utils import safe_unicode

from collective.eeafaceted.batchactions import _


class IBatchActionsFormSchema(model.Schema):

    uids = schema.TextLine(
        title=u"uids",
        description=u''
    )

    referer = schema.TextLine(
        title=u'referer',
        required=False,
    )


class BatchActionForm(EditForm):

    label = _(u"Batch action form")
    fields = Fields(IBatchActionsFormSchema)
    fields['uids'].mode = HIDDEN_MODE
    fields['referer'].mode = HIDDEN_MODE
    ignoreContext = True
    brains = []

    def available(self):
        """Will the action be available for current context?"""
        return True

    def update(self):
        form = self.request.form
        if 'form.widgets.uids' in form:
            uids = form['form.widgets.uids']
        else:
            uids = self.request.get('uids', '')
            form['form.widgets.uids'] = uids

        if 'form.widgets.referer' not in form:
            form['form.widgets.referer'] = self.request.get('referer', '').replace('@', '&').replace('!', '#')

        self.brains = self.brains or brains_from_uids(uids)

        # sort buttons
        self._old_buttons = self.buttons
        self.buttons = self.buttons.select('apply', 'cancel')

    @button.buttonAndHandler(PMF(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.get('HTTP_REFERER'))


def brains_from_uids(uids):
    """ Returns a list of brains from a string containing uids separated by comma """
    uids = uids.split(',')
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(UID=uids)
    return brains


def getAvailableTransitionsVoc(db, brains):
    """ Returns available transitions common for all brains """
    wtool = api.portal.get_tool(name='portal_workflow')
    terms = []
    transitions = None
    for brain in brains:
        obj = brain.getObject()
        if transitions is None:
            transitions = set([(tr['id'], tr['title']) for tr in wtool.getTransitionsFor(obj)])
        else:
            transitions &= set([(tr['id'], tr['title']) for tr in wtool.getTransitionsFor(obj)])
    if transitions:
        for (id, tit) in transitions:
            terms.append(SimpleTerm(id, id, PMF(safe_unicode(tit))))
    return SimpleVocabulary(terms)


class TransitionBatchActionForm(BatchActionForm):

    buttons = BatchActionForm.buttons.copy()
    label = _(u"Batch state change")

    def update(self):
        super(TransitionBatchActionForm, self).update()
        self.voc = getAvailableTransitionsVoc(self.context, self.brains)
        self.fields += Fields(schema.Choice(
            __name__='transition',
            title=_(u'Transition'),
            vocabulary=self.voc,
            description=(len(self.voc) == 0 and
                         _(u'No common or available transition. Modify your selection.') or u''),
            required=len(self.voc) > 0))
        self.fields += Fields(schema.Text(
            __name__='comment',
            title=_(u'Comment'),
            description=_(u'Optional comment to display in history'),
            required=False))

        super(BatchActionForm, self).update()

    @button.buttonAndHandler(_(u'Apply'), name='apply', condition=lambda fi: len(fi.voc))
    def handleApply(self, action):
        """Handle apply button."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
        if data['transition']:
            for brain in self.brains:
                obj = brain.getObject()
                api.content.transition(obj=obj, transition=data['transition'],
                                       comment=self.request.form.get('form.widgets.comment', ''))
        self.request.response.redirect(self.request.form['form.widgets.referer'])
