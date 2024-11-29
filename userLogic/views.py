import string
from lib2to3.fixes.fix_input import context

from django import forms
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView

from analysSentenceLogic.models import Sentence
from userLogic.forms import AcceptInvitationForm
from userLogic.models import CorrectUser
from random import choice

from utils import BaseMixin


@login_required
def get_invite_link(request):
    teacher = CorrectUser.objects.get(id=request.user.id)
    if teacher.student_invite is None:
        teacher.student_invite = "".join([choice(string.ascii_letters + string.digits) for i in range(20)])

        teacher.save()

    return HttpResponseRedirect(reverse("teacher_page"))


class AddStudent2Teacher(BaseMixin, TemplateView, FormView):
    form_class = AcceptInvitationForm
    template_name = "add_student.html"

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("home"))
        code = form.cleaned_data["code"]
        teacher = CorrectUser.objects.filter(student_invite=code)
        if len(teacher) == 0:
            return HttpResponseRedirect(reverse("add_student_link", kwargs={"code": code}))
        teacher = teacher[0]
        if teacher != self.request.user:
            teacher.teacher_students.add(self.request.user)

        return HttpResponseRedirect(reverse("add_student_link", kwargs={"code": code}))

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        teacher = CorrectUser.objects.filter(student_invite=kwargs["code"])
        if len(teacher) == 0:
            return self.get_mixin_context(data)
        teacher = teacher[0]
        data["teacher"] = teacher
        if self.request.user in teacher.teacher_students.all():
            data["already_student"] = True

        return self.get_mixin_context(data)


class RemoveStudentFromTeacher(BaseMixin, TemplateView, FormView):
    form_class = AcceptInvitationForm
    template_name = "remove_student.html"

    def form_valid(self, form):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("teacher_page"))
        id_student = form.cleaned_data["code"]
        teacher = CorrectUser.objects.filter(id=self.request.user.id)
        if len(teacher) == 0:
            return HttpResponseRedirect(reverse("teacher_page"))
        teacher = teacher[0]

        student = teacher.teacher_students.filter(id=id_student)
        if len(student) == 0:
            return HttpResponseRedirect(reverse("teacher_page"))
        student = student[0]

        teacher.teacher_students.remove(student)

        return self.render_to_response(self.get_mixin_context(super().get_context_data(already_remove=student)))

    def get_context_data(self, **kwargs):
        data = super().get_context_data()
        if not self.request.user.is_authenticated:
            return self.get_mixin_context(data)

        teacher = CorrectUser.objects.filter(id=self.request.user.id)
        if len(teacher) == 0 or not kwargs.get("id_student"):
            return self.get_mixin_context(data)

        teacher = teacher[0]

        student_to_remove = teacher.teacher_students.filter(id=kwargs.get("id_student"))
        if len(student_to_remove) == 0:
            return self.get_mixin_context(data)
        student_to_remove = student_to_remove[0]

        data["student_to_remove"] = student_to_remove

        return self.get_mixin_context(data)


def addLike(request, pk):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("home")
        sent = Sentence.objects.filter(id=pk)
        if sent.count() == 0:
            return redirect("home")
        sent = sent[0]

        if sent.dislikes.filter(id=request.user.id).count() > 0:
            sent.dislikes.remove(request.user)

        if sent.likes.filter(id=request.user.id).count() == 0:
            sent.likes.add(request.user)
        else:
            sent.likes.remove(request.user)

        from_page = request.GET.get("from")
        if from_page == "":
            return HttpResponseRedirect(reverse('sentence', kwargs={"pk":sent.id}))
        return HttpResponseRedirect(reverse("view_request")+f"?request={from_page}")


    return redirect("home")



def addDisLike(request, pk):

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("home")

        sent = Sentence.objects.filter(id=pk)

        if sent.count() == 0:
            return redirect("home")
        sent = sent[0]

        if sent.likes.filter(id=request.user.id).count() > 0:
            sent.likes.remove(request.user)

        if sent.dislikes.filter(id=request.user.id).count() == 0:
            sent.dislikes.add(request.user)
        else:
            sent.dislikes.remove(request.user)


        from_page = request.GET.get("from")

        if from_page == "":
            return HttpResponseRedirect(reverse('sentence', kwargs={"pk": sent.id}))

        return HttpResponseRedirect(reverse("view_request") + f"?request={from_page}")


    return redirect("home")



def addFavourite(request, pk):

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("home")

        sent = Sentence.objects.filter(id=pk)
        if sent.count() == 0:
            return redirect("home")
        sent = sent[0]

        if sent.favourites.filter(id=request.user.id).count() == 0:
            sent.favourites.add(request.user)
        else:
            sent.favourites.remove(request.user)

        from_page = request.GET.get("from")
        if from_page == "":
            return HttpResponseRedirect(reverse('sentence', kwargs={"pk": sent.id}))
        return HttpResponseRedirect(reverse("view_request") + f"?request={from_page}")


    return redirect("home")


