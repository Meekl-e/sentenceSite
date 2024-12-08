from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.dateformat import DateFormat

from teacherTasksLogic.models import Task
from userLogic.models import CorrectUser


@login_required
def add_student(request, id_student):
    user = request.user

    task = Task.objects.filter(teacher_id=user.id, apply=False)
    if len(task) == 0:
        return HttpResponseRedirect(reverse("create_task"))
    task = task[0]

    student = user.teacher_students.filter(id=id_student)
    if len(student) == 0:
        return HttpResponseRedirect(reverse("create_task"))
    student = student[0]

    task.students_to.add(student)

    return HttpResponseRedirect(reverse("create_task"))


@login_required
def remove_student(request, id_student):
    user = request.user

    task = Task.objects.filter(teacher_id=user.id, apply=False)
    if len(task) == 0:
        return HttpResponseRedirect(reverse("create_task"))
    task = task[0]

    student = user.teacher_students.filter(id=id_student)
    if len(student) == 0:
        return HttpResponseRedirect(reverse("create_task"))
    student = student[0]

    task.students_to.remove(student)

    return HttpResponseRedirect(reverse("create_task"))


@login_required
def change_date(request):
    task_edit = Task.objects.filter(teacher_id=request.user.id, apply=False)
    if len(task_edit) == 0:
        print("len")
        return HttpResponseRedirect(reverse("create_task"))
    task_edit = task_edit[0]

    new_date = request.GET.get("date")
    if new_date == "inf":
        task_edit.date_expired = task_edit.date_expired.fromisoformat("2099-12-31")
    else:
        try:

            task_edit.date_expired = task_edit.date_expired.fromisoformat(new_date)
        except Exception as e:
            print("error", e)
            return HttpResponseRedirect(reverse("create_task"))
    task_edit.save()

    return HttpResponseRedirect(reverse("create_task"))


@login_required
def change_phrases(request):
    task_edit = Task.objects.filter(teacher_id=request.user.id, apply=False)
    if len(task_edit) == 0:
        print("len")
        return HttpResponseRedirect(reverse("create_task"))
    task_edit = task_edit[0]

    new_val = request.GET.get("value")

    if new_val == "true":
        task_edit.check_phrases = True
        task_edit.save()
    elif new_val == "false":
        task_edit.check_phrases = False
        task_edit.save()

    return HttpResponseRedirect(reverse("create_task"))


@login_required
def change_remove_punctuation(request):
    task_edit = Task.objects.filter(teacher_id=request.user.id, apply=False)
    if len(task_edit) == 0:
        print("len")
        return HttpResponseRedirect(reverse("create_task"))
    task_edit = task_edit[0]

    new_val = request.GET.get("value")

    if new_val == "true":
        task_edit.remove_punctuation = True
        task_edit.save()
    elif new_val == "false":
        task_edit.remove_punctuation = False
        task_edit.save()

    return HttpResponseRedirect(reverse("create_task"))
