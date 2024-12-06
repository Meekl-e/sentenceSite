from analysSentenceLogic.forms import NameForm

class BaseMixin:
    title_page = None
    content = None
    extra_context = {}

    def __init__(self):
        if self.title_page:
            self.extra_context['title'] = self.title_page
        if self.content:
            self.extra_context["content"] = True


    def get_mixin_context(self, context, **kwargs):
        if context.get('sentence_form') is None :
            context["sentence_form"] = NameForm
        context["ad_left"] = ""
        context["ad_right"] = ""
        context.update(kwargs)
        return context
