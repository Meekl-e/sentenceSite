from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import FormView

from analysSentenceLogic.forms import NameForm
from analysSentenceLogic.model_changer import create_sentence
from analysSentenceLogic.models import Sentence
from analysSentenceLogic.sentParsing.parser import parsing, clear_text
from utils import BaseMixin


class checkSentencePage(FormView):
    form_class = NameForm
    template_name = "sentence_result.html"

    def form_valid(self, form):
        text = clear_text(form.cleaned_data["text"])
        candidate = Sentence.objects.exclude(image="").filter(text=text)

        if len(candidate)> 0:
            candidate[0].count += 1
            candidate[0].save()
            return HttpResponseRedirect(reverse("sentence", kwargs={"pk":candidate[0].id}))
        print("PARSING...")
        pars = parsing(text)
        for p in pars:
            id_s = create_sentence(p)
            print(id_s)

        return HttpResponseRedirect(reverse("sentence", kwargs={"pk":id_s}))
    def get(self, request,**kwargs):
        return redirect("home")





class SentencePage(BaseMixin, FormView):
    template_name = "sentence_result.html"
    form_class = NameForm


    def get(self, request, **kwargs):

        res = kwargs["pk"]
        data = super().get_mixin_context(super().get_context_data())
        if res is None:
            return redirect("home")
        sentence = Sentence.objects.filter(id=res)
        if sentence.count() == 0:
            return redirect("home")
        sentence = sentence[0]
        data["pars_result"] = sentence.image
        data["sent_id"] = sentence.id
        data["liked"] = sentence.likes.filter(id=self.request.user.id).count() > 0
        data["disliked"] = sentence.dislikes.filter(id=self.request.user.id).count() > 0
        data["in_fav"] = sentence.favourites.filter(id=self.request.user.id).count() > 0

        return self.render_to_response(data)




