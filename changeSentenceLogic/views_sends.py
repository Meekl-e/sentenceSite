from pprint import pprint

from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from changeSentenceLogic.models import SentenceUnVerified
from changeSentenceLogic.views_save import save_sentence_verified


def accept_sentence(request, sent_id, obj_id):
    if (request.method != "POST" or
            not request.user.is_authenticated):
        return HttpResponseRedirect(reverse("home"))
    form = forms.Form(data=request)
    if form.is_valid():
        data = SentenceUnVerified.objects.filter(id=obj_id)
        if len(data) == 0:
            return redirect("home")

        save_sentence_verified(request, data[0].changed_sentence, sent_id)
        data.delete()

    return HttpResponseRedirect(reverse("teacher_page"))


def remove_sentence_student(request, obj_id):
    if (request.method != "POST" or
            not request.user.is_authenticated):
        return HttpResponseRedirect(reverse("home"))
    form = forms.Form(data=request)
    if form.is_valid():
        data = SentenceUnVerified.objects.filter(id=obj_id)
        if len(data) == 0:
            return redirect("home")
        data.delete()

    return HttpResponseRedirect(reverse("teacher_page"))
