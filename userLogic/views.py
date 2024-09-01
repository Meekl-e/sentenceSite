from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from analysSentenceLogic.models import Sentence


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

        print(sent.likes.count())
        print(sent.dislikes.count())
        return HttpResponseRedirect(reverse('sentence', kwargs={"pk":sent.id}))


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

        print(sent.likes.count())
        print(sent.dislikes.count())
        return HttpResponseRedirect(reverse('sentence', kwargs={"pk":sent.id}))


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


        return HttpResponseRedirect(reverse('sentence', kwargs={"pk":sent.id}))


    return redirect("home")


