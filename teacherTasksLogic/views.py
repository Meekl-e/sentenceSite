from pprint import pprint

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, TemplateView
from spacy.cli import apply
from urllib3 import request

from analysSentenceLogic.forms import NameForm
from analysSentenceLogic.model_changer import create_sentence
from analysSentenceLogic.models import Sentence, MAX_OBJECTS
from analysSentenceLogic.sentParsing.parser import clear_text, text2clear_text, sentence_tokenize, parsing
from studentTasksLogic.models import StudentTask, TaskSentences
from teacherTasksLogic.forms import TaskForm, RemoveTaskForm
from teacherTasksLogic.models import Task
from userLogic.models import CorrectUser
from utils import BaseMixin
from changeSentenceLogic.views_first_stage import words2questions

# Create your views here.


class CreateTask(BaseMixin, FormView):
    template_name = 'create_task.html'
    form_class = NameForm
    success_url = reverse_lazy("create_task")

    def add_sentence(self, text_c, text):
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

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            data = super().get_mixin_context(super().get_context_data())
            return self.render_to_response(context=data)
        text = clear_text(form.cleaned_data["text"])

        text_c, text = text2clear_text(text)

        sentences = sentence_tokenize(text)

        if len(sentences) != 1:
            for s in sentences:
                print(s)
                self.add_sentence(*text2clear_text(s))
            return HttpResponseRedirect(self.success_url)

        self.add_sentence(text_c, text)

        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):

        data = super().get_mixin_context(super().get_context_data())

        if self.request.GET.get("errors"):
            data[self.request.GET.get("errors")] = True

        task_edit = Task.objects.filter(teacher_id=self.request.user.id, apply=False)
        if task_edit.count() != 0:
            task_edit = task_edit[0]
        else:
            task_edit = Task.objects.create(
                teacher_id=self.request.user.id,
            )
        data["sentences"] = [(s.id, s.data[0]) for s in task_edit.sentences.all()]
        if task_edit.check_phrases:
            for id_s, sent in data["sentences"]:
                q_list = []
                for p in sent["simple_sentences_in"]:
                    q_list += [words2questions(p["tokens"][f]["text"], p["tokens"][t]["text"], q) for f, t, q, in
                               p["question_list"]]
                sent["question_list"] = q_list

        in_task_students = task_edit.students_to.all()

        data["students"] = [(student.id, student, student in in_task_students) for student in
                            CorrectUser.objects.get(id=self.request.user.id).teacher_students.all()]
        print(data["students"])

        if task_edit.date_expired.year == 2099:
            data["date_inf"] = "inf"
        else:
            data["date"] = task_edit.date_expired.isoformat()

        data["check_phrases"] = task_edit.check_phrases
        data["remove_punctuation"] = task_edit.remove_punctuation

        return data


class WatchSentence(BaseMixin, TemplateView, LoginRequiredMixin):
    template_name = "watch_sentences.html"

    def get(self, request, *args, **kwargs):
        task_id = kwargs["task_id"]
        student_id = kwargs["student_id"]
        data = super().get_mixin_context(super().get_context_data())

        task = Task.objects.filter(id=task_id, teacher_id=self.request.user.id, apply=True)
        if len(task) == 0:
            print(task_id, self.request.user.id)
            return HttpResponseRedirect(reverse("teacher_page"))
        task = task[0]
        sents_data = TaskSentences.objects.filter(task=task.id, user=student_id)
        stundent = CorrectUser.objects.filter(id=student_id)
        if len(stundent) == 0:
            print("@")
            return HttpResponseRedirect(reverse("teacher_page"))
        stundent = stundent[0]
        data["pars_result"] = []
        for s in sents_data:
            d = s.sentence_data
            d["name"] = stundent.first_name + " " + stundent.last_name
            data["pars_result"].append({"nn_results": [d]})
        data["task_id"] = task_id
        data["from"] = request.GET.get("from")

        return self.render_to_response(data)


class WatchStudent(BaseMixin, TemplateView, LoginRequiredMixin):
    template_name = "watch_students.html"

    def get(self, request, *args, **kwargs):
        student_id = kwargs["student_id"]
        data = super().get_mixin_context(super().get_context_data())

        student = CorrectUser.objects.filter(id=student_id)
        if len(student) == 0:
            return HttpResponseRedirect(reverse("teacher_page"))
        student = student[0]
        data["student"] = student
        tasks = Task.objects.filter(students_to__id=student_id)

        tasks_passed = Task.objects.filter(students_passed__id=student_id)

        data["tasks_passed"] = []
        for t in tasks_passed:
            result = StudentTask.objects.filter(user=student_id, task=t.id)
            if len(result) == 0:
                continue
            result = result[0]
            errors_lst = []
            errors_lst_cnt = []
            checcked = result.result_check[0]
            for k in checcked.keys():
                if type(checcked[k]) is bool or type(checcked[k]) is str:
                    if checcked[k]:
                        errors_lst.append(k)
                elif k != "count":
                    print(checcked[k])
                    if checcked[k] > 0:
                        errors_lst_cnt.append((k, checcked[k]))
            data["tasks_passed"].append(
                (errors_lst, errors_lst_cnt, t)
            )

        data["tasks"] = tasks

        return self.render_to_response(data)


class WatchTask(BaseMixin, TemplateView, LoginRequiredMixin):
    template_name = "watch_task.html"

    def get(self, request, *args, **kwargs):
        task_id = kwargs["task_id"]
        data = super().get_mixin_context(super().get_context_data())

        task = Task.objects.filter(id=task_id, teacher_id=self.request.user.id, apply=True)
        if len(task) == 0:
            return HttpResponseRedirect(reverse("teacher_page"))
        task = task[0]
        students_passed = task.students_passed.all()
        students = []
        for s in students_passed:
            result = StudentTask.objects.filter(user=s.id, task=task_id)
            if len(result) == 0:
                continue
            result = result[0]
            errors_lst = []
            errors_lst_cnt = []
            checcked = result.result_check[0]

            for k in checcked.keys():
                if type(checcked[k]) is bool or type(checcked[k]) is str:
                    if checcked[k]:
                        errors_lst.append(k)
                elif k != "count":
                    print(checcked[k])
                    if checcked[k] > 0:
                        errors_lst_cnt.append((k, checcked[k]))

            students.append({
                "id": s.id,
                "name": s.first_name + " " + s.last_name,
                "all_errors": checcked.get("Всего ошибок"),
                "errors": errors_lst,
                "cnt_errors": errors_lst_cnt,
                "date": result.date
            })
        data["students"] = students
        data["students_to"] = task.students_to.all()

        data["task"] = task

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


class RemoveTask(BaseMixin, TemplateView, FormView, LoginRequiredMixin):
    form_class = RemoveTaskForm
    template_name = "remove_task.html"

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("teacher_page"))
        id_task = form.cleaned_data["task_id"]
        teacher = CorrectUser.objects.filter(id=self.request.user.id)
        if len(teacher) == 0:
            return HttpResponseRedirect(reverse("teacher_page"))
        teacher = teacher[0]

        task = Task.objects.filter(teacher_id=teacher.id, id=id_task, apply=True)
        if len(task) == 0:
            return HttpResponseRedirect(reverse("teacher_page"))
        StudentTask.objects.filter(task=task.id).delete()
        TaskSentences.objects.filter(task=task.id).delete()
        task.delete()

        return self.render_to_response(self.get_mixin_context(super().get_context_data(already_remove=True)))

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        if not self.request.user.is_authenticated:
            return self.get_mixin_context(data)

        teacher = CorrectUser.objects.filter(id=self.request.user.id)
        if len(teacher) == 0 or not kwargs.get("task_id"):
            return self.get_mixin_context(data)

        teacher = teacher[0]

        task_to_remove = Task.objects.filter(id=kwargs.get("task_id"))

        if len(task_to_remove) == 0:
            return self.get_mixin_context(data)
        task_to_remove = task_to_remove[0]
        if task_to_remove.teacher_id != self.request.user.id:
            return self.get_mixin_context(data)
        data["t"] = task_to_remove

        return self.get_mixin_context(data)



class ApplyTask(BaseMixin, TemplateView):
    template_name = "succes_task.html"

    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("create_task"))

        task_edit = Task.objects.filter(teacher_id=self.request.user.id, apply=False)
        if len(task_edit) == 0:
            return HttpResponseRedirect(reverse("create_task"))
        task_edit = task_edit[0]
        if len(task_edit.sentences.all()) == 0:
            return HttpResponseRedirect(reverse("create_task") + "?errors=no_sents")
        if len(task_edit.students_to.all()) == 0:
            return HttpResponseRedirect(reverse("create_task") + "?errors=no_students")

        if Task.objects.filter(apply=True).count() >= MAX_OBJECTS:
            t = Task.objects.filter(apply=True).first()
            StudentTask.objects.filter(task=t.id).delete()
            TaskSentences.objects.filter(task=t.id).delete()
            t.delete()
        task_edit.apply = True
        task_edit.save()
        return self.render_to_response(self.get_mixin_context(super().get_context_data()))
