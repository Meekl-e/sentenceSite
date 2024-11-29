from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, TemplateView
from urllib3 import request

from analysSentenceLogic.forms import NameForm
from analysSentenceLogic.model_changer import create_sentence
from analysSentenceLogic.models import Sentence
from analysSentenceLogic.sentParsing.parser import clear_text, text2clear_text, sentence_tokenize, parsing
from teacherTasksLogic.forms import TaskForm
from teacherTasksLogic.models import Task
from userLogic.models import CorrectUser
from utils import BaseMixin


# Create your views here.

class CreateTask(BaseMixin, FormView):
    template_name = 'create_task.html'
    form_class = NameForm
    success_url = reverse_lazy("create_task")

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            data = super().get_mixin_context(super().get_context_data())
            return self.render_to_response(context=data)
        text = clear_text(form.cleaned_data["text"])

        text_c, text = text2clear_text(text)

        sentences = sentence_tokenize(text)

        if len(sentences) != 1:
            data = super().get_mixin_context(super().get_context_data(error="Пожалуйста, введите одно предложение."))
            return self.render_to_response(context=data)

        candidate = Sentence.objects.filter(text_clear=text_c)

        if candidate.count() > 0:
            candidate[0].count += 1
            sent = candidate[0]
        else:
            sent = Sentence.objects.get(id=create_sentence(parsing(text)))

        task_edit = Task.objects.filter(teacher_id=self.request.user.id, apply=False)
        if task_edit.count() == 0:
            task_edit = Task.objects.create(
                teacher_id=self.request.user.id,
            )
        else:
            task_edit = task_edit[0]
        task_edit.sentences.add(sent)

        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):

        data = super().get_mixin_context(super().get_context_data())

        task_edit = Task.objects.filter(teacher_id=self.request.user.id, apply=False)
        if task_edit.count() != 0:
            data["sentences"] = [(s.id, s.data[0]) for s in task_edit[0].sentences.all()]

        return data


class ChangeElems(BaseMixin, TemplateView):
    template_name = 'change_students.html'

    def get(self, request, **kwargs):

        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("create_task"))
        task_edit = Task.objects.filter(teacher_id=self.request.user.id, apply=False)
        if len(task_edit) == 0:
            return HttpResponseRedirect(reverse("create_task"))
        task_edit = task_edit[0]

        data = super().get_mixin_context(super().get_context_data())

        in_task_students = task_edit.students_to.all()

        data["students"] = [(student.id, student, student in in_task_students) for student in
                            CorrectUser.objects.get(id=request.user.id).teacher_students.all()]

        if task_edit.date_expired.year == 2099:
            data["date_inf"] = "inf"
        else:
            data["date"] = task_edit.date_expired.isoformat()

        data["check_phrases"] = task_edit.check_phrases
        pprint(data)

        return self.render_to_response(data)


def remove_sentence(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("create_task"))

    task_edit = Task.objects.filter(teacher_id=request.user.id, apply=False)
    if len(task_edit) == 0:
        return HttpResponseRedirect(reverse("create_task"))
    task_edit = task_edit[0]
    sent_remove = task_edit.sentences.filter(id=pk)
    if len(sent_remove) != 0:
        task_edit.sentences.remove(sent_remove[0])

    return HttpResponseRedirect(reverse("create_task"))


class ApplyTask(BaseMixin, TemplateView):
    template_name = "succes_task.html"

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("create_task_students"))

        task_edit = Task.objects.filter(teacher_id=self.request.user.id, apply=False)
        if len(task_edit) == 0:
            return HttpResponseRedirect(reverse("create_task_students"))
        task_edit = task_edit[0]
        task_edit.apply = True
        task_edit.save()
        return self.render_to_response(self.get_mixin_context(super().get_context_data()))
