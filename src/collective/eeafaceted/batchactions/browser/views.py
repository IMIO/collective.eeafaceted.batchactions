# -*- coding: utf-8 -*-
"""Batch actions views."""

from AccessControl import Unauthorized
from collective.eeafaceted.batchactions import _
from collective.eeafaceted.batchactions.utils import active_labels
from collective.eeafaceted.batchactions.utils import brains_from_uids
from collective.eeafaceted.batchactions.utils import cannot_modify_field_msg
from collective.eeafaceted.batchactions.utils import has_interface
from collective.eeafaceted.batchactions.utils import is_permitted
from operator import attrgetter
from plone import api
from plone.formwidget.masterselect import MasterSelectField
from plone.supermodel import model
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFPlone.utils import safe_unicode
from z3c.form import button
from z3c.form.browser.select import SelectFieldWidget
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.i18n import translate
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


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


try:
    from ftw.labels.interfaces import ILabeling
    from ftw.labels.interfaces import ILabelJar
    from ftw.labels.interfaces import ILabelSupport
except ImportError:
    pass


class LabelsBatchActionForm(BaseBatchActionForm):

    label = _(u"Batch labels change")
    weight = 20

    def get_labeljar_context(self):
        return self.context

    def get_labels_vocabulary(self):
        terms, p_labels, g_labels = [], [], []
        context = self.get_labeljar_context()
        try:
            adapted = ILabelJar(context)
        except:
            return SimpleVocabulary(terms), [], []
        self.can_change_labels = is_permitted(self.brains, perm='ftw.labels: Change Labels')
        for label in adapted.list():
            if label['by_user']:
                p_labels.append(label['label_id'])
                terms.append(SimpleVocabulary.createTerm('%s:' % label['label_id'],
                                                         label['label_id'],
                                                         u'{} (*)'.format(safe_unicode(label['title']))))
            else:
                g_labels.append(label['label_id'])
                if self.can_change_labels:
                    terms.append(SimpleVocabulary.createTerm(label['label_id'], label['label_id'],
                                                             safe_unicode(label['title'])))
        return SimpleVocabulary(terms), set(p_labels), g_labels

    def _update(self):
        labels_voc, self.p_labels, self.g_labels = self.get_labels_vocabulary()
        self.do_apply = len(labels_voc._terms) and has_interface(self.brains, ILabelSupport)
        self.fields += Fields(MasterSelectField(
            __name__='action_choice',
            title=_(u'Batch action choice'),
            description=(not self.do_apply and cannot_modify_field_msg or u''),
            vocabulary=SimpleVocabulary([SimpleTerm(value=u'add', title=_(u'Add items')),
                                         SimpleTerm(value=u'remove', title=_(u'Remove items')),
                                         SimpleTerm(value=u'replace', title=_(u'Replace some items by others')),
                                         SimpleTerm(value=u'overwrite', title=_(u'Overwrite'))]),
            slave_fields=(
                {'name': 'removed_values',
                 'slaveID': '#form-widgets-removed_values',
                 'action': 'hide',
                 'hide_values': (u'add', u'overwrite'),
                 'siblings': True,
                 },
                {'name': 'added_values',
                 'slaveID': '#form-widgets-added_values',
                 'action': 'hide',
                 'hide_values': (u'remove'),
                 'siblings': True,
                 },
            ),
            required=self.do_apply,
            default=u'add'
        ))
        if self.do_apply:
            self.fields += Fields(schema.List(
                __name__='removed_values',
                title=_(u"Removed values"),
                description=_(u"Select the values to remove (CTRL+click). A personal label is represented by (*)."),
                required=False,
                value_type=schema.Choice(vocabulary=labels_voc),
            ))
            self.fields += Fields(schema.List(
                __name__='added_values',
                title=_(u"Added values"),
                description=_(u"Select the values to add (CTRL+click). A personal label is represented by (*)."),
                required=False,
                value_type=schema.Choice(vocabulary=labels_voc),
            ))
            self.fields["removed_values"].widgetFactory = SelectFieldWidget
            self.fields["added_values"].widgetFactory = SelectFieldWidget

    def _update_widgets(self):
        if self.do_apply:
            #        self.widgets['action_choice'].size = 4
            self.widgets['removed_values'].multiple = 'multiple'
            self.widgets['removed_values'].size = 5
            self.widgets['added_values'].multiple = 'multiple'
            self.widgets['added_values'].size = 5

    def _apply(self, **data):
        if ((data.get('removed_values', None) and data['action_choice'] in ('remove', 'replace')) or
           (data.get('added_values', None)) and data['action_choice'] in ('add', 'replace', 'overwrite')):
            values = {'p_a': [], 'p_r': [], 'g_a': [], 'g_r': []}
            for act, lst in (('a', data.get('added_values', [])), ('r', data.get('removed_values', []))):
                for val in lst:
                    typ = (':' in val) and 'p' or 'g'
                    values['{}_{}'.format(typ, act)].append(val.split(':')[0])
            for brain in self.brains:
                obj = brain.getObject()
                labeling = ILabeling(obj)
                p_act, g_act = active_labels(labeling)
                # manage global labels
                if self.can_change_labels and (values['g_a'] or values['g_r']):
                    if data['action_choice'] in ('overwrite'):
                        items = set(values['g_a'])
                    else:
                        items = set(g_act)  # currently active labels
                        if data['action_choice'] in ('remove', 'replace'):
                            items = items.difference(values['g_r'])
                        if data['action_choice'] in ('add', 'replace'):
                            items = items.union(values['g_a'])
                    labeling.update(items)
                # manage personal labels
                if values['p_a'] or values['p_r']:
                    if data['action_choice'] in ('overwrite'):
                        items = set(values['p_a'])
                        labeling.pers_update(self.p_labels.difference(items), False)
                        labeling.pers_update(items, True)
                    else:
                        if data['action_choice'] in ('remove', 'replace'):
                            labeling.pers_update(set(p_act).intersection(values['p_r']), False)
                        if data['action_choice'] in ('add', 'replace'):
                            labeling.pers_update(values['p_a'], True)
                obj.reindexObject(['labels'])
