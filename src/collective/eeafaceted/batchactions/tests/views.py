from collective.eeafaceted.batchactions.browser.views import BatchActionForm


class TestingBatchActionForm(BatchActionForm):

    buttons = BatchActionForm.buttons.copy()
    label = (u"Testing form")

    def available(self):
        """Available if 'hide_testing_action' not found in request."""
        if not self.request.get('hide_testing_action'):
            return True
        return False
