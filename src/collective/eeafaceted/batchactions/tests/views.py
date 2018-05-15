from collective.eeafaceted.batchactions.browser.views import BaseBatchActionForm


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
