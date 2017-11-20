from collective.eeafaceted.batchactions.browser.views import BatchActionForm


class TestingBatchActionForm(BatchActionForm):

    buttons = BatchActionForm.buttons.copy()
    label = (u"Testing form")
