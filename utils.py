
from authLogic.forms import LoginForm
from analysSentenceLogic.forms import NameForm

class BaseMixin:
    title_page = None
    entrance = None
    extra_context = {}

    def __init__(self):
        if self.title_page:
            self.extra_context['title'] = self.title_page
        if self.entrance:
            self.extra_context['entrance'] = self.entrance


    def get_mixin_context(self, context, **kwargs):
        if context.get('auth_form') is None :
            context["auth_form"] = LoginForm
        if context.get('sentence_form') is None :
            context["sentence_form"] = NameForm
        context.update(kwargs)
        return context
