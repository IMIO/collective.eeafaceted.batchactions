from collective.eeafaceted.batchactions.browser.views import BatchActionForm


class TestingBatchActionForm(BatchActionForm):

    buttons = BatchActionForm.buttons.copy()
    label = (u"Testing form")
    button_with_icon = True

    def available(self):
        """Available if 'hide_testing_action' not found in request."""
        res = super(TestingBatchActionForm, self).available()
        if res and not self.request.get('hide_testing_action'):
            return True
        return False
