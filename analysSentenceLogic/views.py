import random

from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import FormView

from analysSentenceLogic.forms import NameForm
from analysSentenceLogic.model_changer import create_sentence
from analysSentenceLogic.models import Sentence
from analysSentenceLogic.sentParsing.parser import parsing, clear_text, TokenDefault, sentence_tokenize
from utils import BaseMixin
import random as rnd
import string


class checkSentencePage(FormView):
    form_class = NameForm
    template_name = "sentence_result.html"

    def form_valid(self, form):
        text = clear_text(form.cleaned_data["text"])
        sentences = sentence_tokenize(text)
        if len(sentences) == 1:
            candidate = Sentence.objects.filter(text=text)
            if len(candidate) > 0:
                candidate[0].count += 1
                candidate[0].save()
                return HttpResponseRedirect(reverse("sentence", kwargs={"pk": candidate[0].id}))
            print("PARSING...")
            id_sent = create_sentence(parsing(text))
            print(id_sent)
            return HttpResponseRedirect(reverse("sentence", kwargs={"pk": id_sent}))

        id_request = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(50))
        print(id_request)
        return HttpResponseRedirect(reverse("view_request")+"?request=" + id_request)


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
        #print(type(sentence.tokens))
        data["pars_result"] = sentence.data #sentence.tokens.all()
        data["sent_id"] = sentence.id
        data["liked"] = sentence.likes.filter(id=self.request.user.id).count() > 0
        data["disliked"] = sentence.dislikes.filter(id=self.request.user.id).count() > 0
        data["in_fav"] = sentence.favourites.filter(id=self.request.user.id).count() > 0

        return self.render_to_response(data)





class ViewRequest(BaseMixin, FormView):
    template_name = "sentence_result.html"
    form_class = NameForm


    def get(self, request, **kwargs):
        id_request = request.GET.get("request")
        if id_request is None:
            return redirect("home")

        return self.render_to_response({})
