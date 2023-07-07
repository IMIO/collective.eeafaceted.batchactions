# -*- coding: utf-8 -*-

from collective.contact.widget.schema import ContactChoice
from collective.contact.widget.source import ContactSourceBinder
from collective.eeafaceted.batchactions.browser.views import BaseARUOBatchActionForm
from collective.eeafaceted.batchactions.browser.views import BaseBatchActionForm
from collective.eeafaceted.batchactions.browser.views import ContactBaseBatchActionForm
from imio.helpers.content import get_vocab


class TestingBatchActionForm(BaseBatchActionForm):

    buttons = BaseBatchActionForm.buttons.copy()
    label = (u"Testing form")
    button_with_icon = True
    overlay = False

    def available(self):
        """Available if 'hide_testing_action' not found in request."""
        res = super(TestingBatchActionForm, self).available()
        if res and not self.request.get('hide_testing_action'):
            return True
        return False


class ContactBatchActionForm(ContactBaseBatchActionForm):

    available_permission = 'Manage portal'
    attribute = 'related_organizations'
    field_value_type = ContactChoice(source=ContactSourceBinder(portal_type="organization"))


class TestingARUOBatchActionForm(BaseARUOBatchActionForm):

    modified_attr_name = 'custom_portal_types'
    indexes = 'custom_portal_types'
    call_modified_event = True
    required = True

    def _vocabulary(self):
        return get_vocab(self.context, 'plone.app.vocabularies.PortalTypes')
