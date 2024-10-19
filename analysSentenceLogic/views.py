import random as rnd
import string

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from analysSentenceLogic.forms import NameForm
from analysSentenceLogic.model_changer import create_sentence, save_to_request
from analysSentenceLogic.models import Sentence, RequestSentences
from analysSentenceLogic.sentParsing.parser import parsing, clear_text, sentence_tokenize, text2clear_text
from utils import BaseMixin


class checkSentencePage(FormView):
    form_class = NameForm
    template_name = "sentence_result.html"

    def form_valid(self, form):
        text = clear_text(form.cleaned_data["text"])

        text_c, text = text2clear_text(text)

        sentences = sentence_tokenize(text)
        if len(sentences) == 1:

            candidate = Sentence.objects.filter(text_clear=text_c)
            if candidate.count() > 0:
                candidate[0].count += 1
                candidate[0].save()
                return HttpResponseRedirect(reverse("sentence", kwargs={"pk": candidate[0].id}))
            print("PARSING...")
            id_sent = create_sentence(parsing(text))
            # print(id_sent)
            return HttpResponseRedirect(reverse("sentence", kwargs={"pk": id_sent}))


        id_request = "".join(rnd.choice(string.ascii_lowercase + string.digits) for _ in range(5))
        ids_sents = []
        for sentence in sentences:
            text_c, sentence = text2clear_text(sentence)
            sentence_candidates = Sentence.objects.filter(text_clear=text_c)
            if sentence_candidates.count() > 0:
                id_sent = sentence_candidates[0].id

            else:
                id_sent = create_sentence(parsing(sentence))
            ids_sents.append(id_sent)
        save_to_request(request=id_request, id_sents=ids_sents)
        return HttpResponseRedirect(reverse("view_request")+"?request=" + id_request)


    def get(self, request,**kwargs):
        return redirect("home")





class SentencePage(BaseMixin, FormView):
    template_name = "sentence_result.html"
    form_class = NameForm


    def get(self, request, **kwargs):

        res = kwargs["pk"]
        if res is None:
            return redirect("home")
        data = super().get_mixin_context(super().get_context_data())
        sentence = Sentence.objects.filter(id=res)
        if sentence.count() == 0:
            return redirect("home")
        sentence = sentence[0]
        #print(type(sentence.tokens))
        data["pars_result"] = [{
            "nn_results": sentence.data,
            "sent_id": sentence.id,
            "liked": sentence.likes.filter(id=self.request.user.id).count() > 0,
            "disliked": sentence.dislikes.filter(id=self.request.user.id).count() > 0,
            "in_fav": sentence.favourites.filter(id=self.request.user.id).count() > 0,
        }]

        return self.render_to_response(data)





class ViewRequest(BaseMixin, FormView):
    template_name = "sentence_result.html"
    form_class = NameForm


    def get(self, request, **kwargs):
        id_request = request.GET.get("request")

        if id_request is None:
            return redirect("home")
        data = super().get_mixin_context(super().get_context_data())

        try:
            obj = RequestSentences.objects.get(id_request=id_request)
        except:
            return redirect("home")

        data["pars_result"] = []
        data["from_request"] = id_request

        count = 0
        for s in obj.request_sentences.all():
            data["pars_result"].append({
                "nn_results": s.data,
                "sent_id":s.id,
                "id_request": id_request,
                "liked": s.likes.filter(id=self.request.user.id).count() > 0,
                "disliked": s.dislikes.filter(id=self.request.user.id).count() > 0,
                "in_fav": s.favourites.filter(id=self.request.user.id).count() > 0,
            })

            count += 1


        return self.render_to_response(data)
