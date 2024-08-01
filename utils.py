
from authLogic.forms import LoginForm

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
        context.update(kwargs)
        return context
