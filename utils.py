from analysSentenceLogic.forms import NameForm
from analysSentenceLogic.models import Sentence
from teacherTasksLogic.models import Task
from userLogic.models import CorrectUser


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
        context["count_students"] = CorrectUser.objects.filter(role="student").count()
        context["count_teachers"] = CorrectUser.objects.filter(role="teachers").count()
        context["count_sentences"] = Sentence.objects.count()
        context["count_tasks"] = Task.objects.count()
        context.update(kwargs)
        return context
