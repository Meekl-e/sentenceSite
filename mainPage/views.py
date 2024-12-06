from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import *

from analysSentenceLogic.models import Sentence
from teacherTasksLogic.models import Task
from userLogic.models import CorrectUser
from utils import BaseMixin


# Create your views here.

class homePage(BaseMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context["content"] = True
        return self.get_mixin_context(context)


class profilePage(BaseMixin, TemplateView):
    template_name = 'profile.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        return self.render_to_response(self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):

        context = super().get_context_data()
        if self.request.user.is_authenticated:
            context["user"] = self.request.user
            if self.request.user.change_sentence and len(self.request.user.change_sentence) > 0:
                sents = self.request.user.change_sentence.keys()
                all_texts = []
                for k in sents:
                    sent_text = Sentence.objects.filter(id=k)
                    if len(sent_text) != 0:
                        sent_text = sent_text[0].text
                        all_texts.append(sent_text)
                context["sents"] = zip(sents, all_texts)

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
        if not self.request.user.is_authenticated:
            return self.get_mixin_context(context)
        student = CorrectUser.objects.get(id=self.request.user.id)
        context["teachers"] = CorrectUser.objects.filter(teacher_students__id=student.id)
        context["tasks"] = Task.objects.filter(apply=True, students_to__id=student.id)
        context["favourites"] = student.favourites.all()
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
        context["favourites"] = teacher.favourites.all()
        return self.get_mixin_context(context)




