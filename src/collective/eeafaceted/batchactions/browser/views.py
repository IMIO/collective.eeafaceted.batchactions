# -*- coding: utf-8 -*-
"""Batch actions views."""

from operator import attrgetter

from AccessControl import Unauthorized
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from plone import api
from plone.supermodel import model
from z3c.form.form import Form
from z3c.form import button
from z3c.form.field import Fields
from z3c.form.interfaces import HIDDEN_MODE
from zope.i18n import translate
from Products.CMFPlone import PloneMessageFactory as PMF

from collective.eeafaceted.batchactions import _
from collective.eeafaceted.batchactions.utils import brains_from_uids


class IBaseBatchActionsFormSchema(model.Schema):

    uids = schema.TextLine(
        title=u"uids",
        description=u''
    )

    referer = schema.TextLine(
        title=u'referer',
        required=False,
    )


class BaseBatchActionForm(Form):

    label = _(u"Batch action form")
    fields = Fields(IBaseBatchActionsFormSchema)
    fields['uids'].mode = HIDDEN_MODE
    fields['referer'].mode = HIDDEN_MODE
    ignoreContext = True
    brains = []
    do_apply = True
    # this will add a specific class to the generated button action
    # so it is possible to skin it with an icon
    button_with_icon = False
    overlay = True
    weight = 100

    def available(self):
        """Will the action be available for current context?"""
        return True

    def _update(self):
        """Method to override if you need to do something in the update."""
        return

    def _update_widgets(self):
        """Method to override if you need to do something after the updateWidgets method."""
        return

    @property
    def description(self):
        """ """
        # update description depending on number of brains
        return _('This action will affect ${number} element(s).',
                 mapping={'number': len(self.brains)})

    def _apply(self, **data):
        """This method receives in data the form content and does the apply logic.
           It is the method to implement if default handleApply is enough."""
        raise NotImplementedError

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
        self._update()
        super(BaseBatchActionForm, self).update()
        self._update_widgets()

    @button.buttonAndHandler(_(u'Apply'), name='apply', condition=lambda fi: fi.do_apply)
    def handleApply(self, action):
        """ """
        if not self.available():
            raise Unauthorized

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
        else:
            # call the method that does the job
            self._apply(**data)
            self.request.response.redirect(self.request.form['form.widgets.referer'])

    @button.buttonAndHandler(PMF(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        self.request.response.redirect(self.request.get('HTTP_REFERER'))


class TransitionBatchActionForm(BaseBatchActionForm):

    label = _(u"Batch state change")
    weight = 10

    def getAvailableTransitionsVoc(self):
        """ Returns available transitions common for all brains """
        wtool = api.portal.get_tool(name='portal_workflow')
        terms = []
        transitions = None
        for brain in self.brains:
            obj = brain.getObject()
            if transitions is None:
                transitions = set([(tr['id'], tr['title']) for tr in wtool.getTransitionsFor(obj)])
            else:
                transitions &= set([(tr['id'], tr['title']) for tr in wtool.getTransitionsFor(obj)])
        if transitions:
            for (id, tit) in transitions:
                terms.append(
                    SimpleTerm(id,
                               id,
                               translate(tit,
                                         domain='plone',
                                         context=self.request)))
        terms = sorted(terms, key=attrgetter('title'))
        return SimpleVocabulary(terms)

    def _update(self):
        self.voc = self.getAvailableTransitionsVoc()
        self.do_apply = len(self.voc) > 0
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

    def _apply(self, **data):
        """ """
        if data['transition']:
            for brain in self.brains:
                obj = brain.getObject()
                api.content.transition(obj=obj,
                                       transition=data['transition'],
                                       comment=data['comment'])
