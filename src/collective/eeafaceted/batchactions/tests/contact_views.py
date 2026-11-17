# -*- coding: utf-8 -*-

from collective.contact.widget.schema import ContactChoice
from collective.contact.widget.source import ContactSourceBinder
from collective.eeafaceted.batchactions.browser.views import ContactBaseBatchActionForm


class ContactBatchActionForm(ContactBaseBatchActionForm):

    available_permission = "Manage portal"
    attribute = "related_organizations"
    field_value_type = ContactChoice(
        source=ContactSourceBinder(portal_type="organization")
    )
