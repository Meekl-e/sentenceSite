from django.urls import reverse
from django.views.generic import *

from analysSentenceLogic.forms import NameForm
from analysSentenceLogic.models import Sentence
from userLogic.models import CorrectUser
from utils import BaseMixin


# Create your views here.

class homePage(BaseMixin, ListView):
    template_name = 'index.html'
    model = Sentence
    context_object_name = 'sentences'
    queryset = Sentence.objects.exclude(count=1).order_by('-count')[:5]


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return self.get_mixin_context(context )





class aboutPage(BaseMixin, TemplateView):
    template_name = 'about.html'



    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return self.get_mixin_context(context)



class studentPage(BaseMixin, TemplateView):
    template_name = 'student.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return self.get_mixin_context(context)


class teacherPage(BaseMixin, TemplateView):
    template_name = 'teacher.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        if not self.request.user.is_authenticated:
            return self.get_mixin_context(context)
        teacher = CorrectUser.objects.get(id=self.request.user.id)
        context["teacher"] = teacher
        if teacher.student_invite:
            context["students_link"] = self.request.build_absolute_uri(
                reverse('add_student_link', kwargs={"code": teacher.student_invite}))
        context["students"] = teacher.teacher_students.all()
        return self.get_mixin_context(context)




