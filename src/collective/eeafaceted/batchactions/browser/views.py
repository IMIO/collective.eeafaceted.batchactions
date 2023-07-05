# -*- coding: utf-8 -*-
"""Batch actions views."""

from AccessControl import Unauthorized
from collective.eeafaceted.batchactions import _
from collective.eeafaceted.batchactions.utils import active_labels
from collective.eeafaceted.batchactions.utils import brains_from_uids
from collective.eeafaceted.batchactions.utils import cannot_modify_field_msg
from collective.eeafaceted.batchactions.utils import has_interface
from collective.eeafaceted.batchactions.utils import is_permitted
from imio.helpers.content import safe_encode
from imio.helpers.security import check_zope_admin
from imio.helpers.security import fplog
from imio.helpers.workflow import update_role_mappings_for
from imio.pyutils.utils import sort_by_indexes
from operator import attrgetter
from plone import api
from plone.formwidget.masterselect import MasterSelectField
from plone.supermodel import model
from Products.CMFCore.permissions import DeleteObjects
from Products.CMFCore.utils import _checkPermission
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.CMFPlone.utils import safe_unicode
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.field import Fields
from z3c.form.form import Form
from z3c.form.interfaces import HIDDEN_MODE
from zope import schema
from zope.component import getUtility
from zope.i18n import translate
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import modified
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
    # easy way to hide the "Apply" button when required conditions
    # are not met for the action to be applied
    do_apply = True
    # the title of the apply button to fit current action
    apply_button_title = None
    # this will add a specific class to the generated button action
    # so it is possible to skin it with an icon
    button_with_icon = False
    overlay = True
    weight = 100
    # by default, action is available or if a permission is defined
    available_permission = ''
    # make action only available to the Zope admin
    available_for_zope_admin = False
    # useful when dispalying batch actions on several views for same context
    section = "default"

    def available(self):
        """Will the action be available for current context?"""
        res = True
        if self.available_permission:
            res = api.user.has_permission(self.available_permission, obj=self.context)
        elif self.available_for_zope_admin:
            res = check_zope_admin()
        return res

    def _update(self):
        """Method to override if you need to do something in the update."""
        return

    def _final_update(self):
        """Method to override if you need to do something when everything have been updated."""
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
        if self.apply_button_title is not None and 'apply' in self.actions:
            self.actions['apply'].title = self.apply_button_title
        self._final_update()

    @button.buttonAndHandler(_(u'Apply'), name='apply', condition=lambda fi: fi.do_apply)
    def handleApply(self, action):
        """ """
        if not self.available():
            raise Unauthorized

        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
        else:
            # log in fingerpointing before executing job
            extras = 'action={0} number_of_elements={1}'.format(
                repr(self.label), len(self.brains))
            fplog('apply_batch_action', extras=extras)
            # call the method that does the job
            applied = self._apply(**data)
            # redirect if not using an overlay
            if not self.request.form.get('ajax_load', ''):
                self.request.response.redirect(safe_encode(self.request.form['form.widgets.referer']))
            else:
                # make sure we return nothing, taken into account by ajax query
                if not applied:
                    self.request.RESPONSE.setStatus(204)
                return applied or ""

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
                               translate(safe_unicode(tit, 'utf8'),
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


class DeleteBatchActionForm(BaseBatchActionForm):

    label = _(u"Delete elements")
    weight = 5
    button_with_icon = True
    apply_button_title = _('delete-batch-action-but')

    def _get_deletable_elements(self):
        """ """
        deletables = [obj for obj in self.objs
                      if _checkPermission(DeleteObjects, obj)]
        return deletables

    def _update(self):
        """ """
        self.objs = [brain.getObject() for brain in self.brains]
        self.deletables = self._get_deletable_elements()

    @property
    def description(self):
        """ """
        if len(self.deletables) < len(self.brains):
            not_deletables = len(self.brains) - len(self.deletables)
            return _('This action will only affect ${deletable_number} element(s), indeed '
                     'you do not have the permission to delete ${not_deletable_number} element(s).',
                     mapping={'deletable_number': len(self.deletables),
                              'not_deletable_number': not_deletables, })
        else:
            return super(DeleteBatchActionForm, self).description

    def _apply(self, **data):
        """ """
        for obj in self.deletables:
            api.content.delete(obj)


class UpdateWFRoleMappingsActionForm(BaseBatchActionForm):

    label = _(u"Update WF role mappings")
    available_for_zope_admin = True

    def _apply(self, **data):
        """ """
        wtool = api.portal.get_tool(name='portal_workflow')
        for brain in self.brains:
            obj = brain.getObject()
            for wf in wtool.getWorkflowsFor(obj):
                update_role_mappings_for(obj, wf=wf)


try:
    from ftw.labels.interfaces import ILabeling
    from ftw.labels.interfaces import ILabelJar
    from ftw.labels.interfaces import ILabelSupport
except ImportError:
    pass


class BaseARUOBatchActionForm(BaseBatchActionForm):
    """Base class for "add/remove/update/overwrite" actions."""

    @property
    def _vocabulary(self):
        """A SimpleVocabulary instance."""
        return None

    def _should_keep_vocabulary_order(self):
        """Make order of stored values respect field vocabulary terms order?"""
        return True

    @property
    def _modified_attr_name(self):
        """The name of the attribute that will be modified on the object."""
        return None

    @property
    def _removed_values_description(self):
        """The translated description of the "removed_values" field."""
        return _(u"Select the values to remove.")

    @property
    def _added_values_description(self):
        """The translated description of the "added_values" field."""
        return _(u"Select the values to add.")

    @property
    def _may_apply(self):
        """The condition for the action to be applied."""
        return is_permitted(self.brains)

    @property
    def _indexes(self):
        """Return list of indexes to reindex if any."""
        return []

    @property
    def _should_call_modified_event(self):
        """Call the "modified" event on object at the end if it was modified?"""
        return False

    def _update(self):
        self.do_apply = self._may_apply
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
                description=self._removed_values_description,
                required=False,
                value_type=schema.Choice(vocabulary=self._vocabulary),
            ))
            self.fields += Fields(schema.List(
                __name__='added_values',
                title=_(u"Added values"),
                description=self._added_values_description,
                required=False,
                value_type=schema.Choice(vocabulary=self._vocabulary),
            ))
            self.fields["removed_values"].widgetFactory = CheckBoxFieldWidget
            self.fields["added_values"].widgetFactory = CheckBoxFieldWidget

    def _update_widgets(self):
        if self.do_apply:
            self.widgets['removed_values'].multiple = 'multiple'
            self.widgets['removed_values'].size = 5
            self.widgets['added_values'].multiple = 'multiple'
            self.widgets['added_values'].size = 5

    def _apply(self, **data):
        if ((data.get('removed_values', None) and data['action_choice'] in ('remove', 'replace')) or
           (data.get('added_values', None)) and data['action_choice'] in ('add', 'replace', 'overwrite')):
            for brain in self.brains:
                obj = brain.getObject()
                if data['action_choice'] in ('overwrite', ):
                    items = set(data['added_values'])
                else:
                    items = set(getattr(obj, self._modified_attr_name, []))
                    if data['action_choice'] in ('remove', 'replace'):
                        items = items.difference(data['removed_values'])
                    if data['action_choice'] in ('add', 'replace'):
                        items = items.union(data['added_values'])
                # only update if values changed
                if list(getattr(obj, self._modified_attr_name)) != list(items):
                    if self._should_keep_vocabulary_order:
                        vocab = self.fields['added_values'].field.value_type.vocabulary
                        all_values = [term.value for term in vocab._terms]
                        indexes = [all_values.index(item) for item in items]
                        items = sort_by_indexes(list(items), indexes)
                    setattr(obj, self._modified_attr_name, items)
                    if self._should_call_modified_event:
                        # will also reindex the entire object
                        modified(obj)
                    elif self._indexes:
                        obj.reindexObject(idxs=self._indexes)


class LabelsBatchActionForm(BaseARUOBatchActionForm):

    label = _(u"Batch labels change")
    weight = 20

    @property
    def _vocabulary(self):
        return self.labels_voc

    @property
    def _removed_values_description(self):
        return _(u"Select the values to remove. A personal label is represented by (*).")

    @property
    def _added_values_description(self):
        return _(u"Select the values to add. A personal label is represented by (*).")

    @property
    def _may_apply(self):
        self.labels_voc, self.p_labels, self.g_labels = self.get_labels_vocabulary()
        return len(self.labels_voc._terms) and has_interface(self.brains, ILabelSupport)

    def get_labeljar_context(self):
        return self.context

    def get_labels_vocabulary(self):
        terms, p_labels, g_labels = [], [], []
        context = self.get_labeljar_context()
        try:
            adapted = ILabelJar(context)
        except Exception:
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


try:
    from collective.contact.widget.schema import ContactList
    from z3c.relationfield.relation import RelationValue
except ImportError:
    pass


class ContactBaseBatchActionForm(BaseBatchActionForm):
    """
        Base class to manage contact field change.
        For now, only ContactList.
    """

    label = _(u"Batch contact field change")
    weight = 30
    attribute = ''
    field_value_type = None

    def _update(self):
        assert self.attribute
        assert self.field_value_type is not None
        self.do_apply = is_permitted(self.brains)
        self.fields += Fields(schema.Choice(
            __name__='action_choice',
            title=_(u'Batch action choice'),
            description=(not self.do_apply and cannot_modify_field_msg or u''),
            vocabulary=SimpleVocabulary([SimpleTerm(value=u'add', title=_(u'Add items')),
                                         SimpleTerm(value=u'remove', title=_(u'Remove items')),
                                         SimpleTerm(value=u'replace', title=_(u'Replace some items by others')),
                                         SimpleTerm(value=u'overwrite', title=_(u'Overwrite'))]),
            required=self.do_apply,
            default=u'add'
        ))
        if self.do_apply:
            self.fields += Fields(ContactList(
                __name__='removed_values',
                title=_(u"Removed values"),
                description=_(u"Search and select the values to remove, if necessary."),
                required=False,
                addlink=False,
                value_type=self.field_value_type,
            ))
            self.fields += Fields(ContactList(
                __name__='added_values',
                title=_(u"Added values"),
                description=_(u"Search and select the values to add."),
                required=False,
                addlink=False,
                value_type=self.field_value_type,
            ))

    def _apply(self, **data):
        if ((data.get('removed_values', None) and data['action_choice'] in ('remove', 'replace')) or
           (data.get('added_values', None)) and data['action_choice'] in ('add', 'replace', 'overwrite')):
            intids = getUtility(IIntIds)
            for brain in self.brains:
                obj = brain.getObject()
                if data['action_choice'] in ('overwrite'):
                    items = set(data['added_values'])
                else:
                    # we get the linked objects
                    items = set([intids.getObject(rel.to_id) for rel in (getattr(obj, self.attribute) or [])
                                 if not rel.isBroken()])
                    if data['action_choice'] in ('remove', 'replace'):
                        items = items.difference(data['removed_values'])
                    if data['action_choice'] in ('add', 'replace'):
                        items = items.union(data['added_values'])
                # transform to relations
                rels = [RelationValue(intids.getId(ob)) for ob in items]
                setattr(obj, self.attribute, rels)
                modified(obj)
