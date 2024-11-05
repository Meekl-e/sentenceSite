from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView

from analysSentenceLogic.models import Sentence, Parent_to_children
from analysSentenceLogic.sentParsing.parser import get_word_tokenize
from utils import BaseMixin
from .forms import *


def words2questions(w_from, w_to, question) -> str:
    return w_from + f" == {question.capitalize()} ==> " + w_to

class ChangeSentence(BaseMixin, TemplateView):
    template_name = "change_sentence.html"

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": kwargs["pk"]}))

        kwargs["pk"] = str(kwargs["pk"])


        formset = WordFormSet(request.POST)

        question_form = RelationForm(data=request.POST)


        if not formset.is_valid() or not question_form.is_valid():
            print("Formset", formset.errors)
            print("Question", question_form.errors)
            print( question_form.is_valid())
            data = super().get_mixin_context(super().get_context_data(formset=formset, question_form=question_form))
            return self.render_to_response(context=data)

        try:
            from_i, to_i = map(int, question_form.cleaned_data["selected"].split("-"))
        except Exception:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": kwargs["pk"]}))


        lined = [form.cleaned_data["type"] for form in formset]
        question = question_form.cleaned_data["question"]
        tokens = question_form.cleaned_data["tokens"].split()



        if not request.user.change_sentence:
            request.user.change_sentence = {}


        if not request.user.change_sentence.get(kwargs["pk"]):
            request.user.change_sentence[kwargs["pk"]] = {}

        if not request.user.change_sentence[kwargs["pk"]].get("question_list"):
            request.user.change_sentence[kwargs["pk"]]["question_list"] = []
            request.user.change_sentence[kwargs["pk"]]["text_question_list"] = []


        append = True

        for f, t, q in request.user.change_sentence[kwargs["pk"]]["question_list"]:
            if f == from_i and t == to_i and q.lower()==question.lower():
                append = False

        if append:
            for i in range(len(request.user.change_sentence[kwargs["pk"]]["question_list"])):
                o = request.user.change_sentence[kwargs["pk"]]["question_list"][i]
                if o[0] == from_i and o[1] == to_i:
                    request.user.change_sentence[kwargs["pk"]]["question_list"].pop(i)
                    request.user.change_sentence[kwargs["pk"]]["text_question_list"].pop(i)
                    request.user.save()
                    break

        request.user.change_sentence[kwargs["pk"]]["lined"] = lined
        if append:
            token_from, token_to = tokens[from_i], tokens[to_i]
            request.user.change_sentence[kwargs["pk"]]["text_question_list"].append(words2questions(token_from, token_to, question))
            request.user.change_sentence[kwargs["pk"]]["question_list"].append((from_i, to_i, question.capitalize()))





        request.user.save()


        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": kwargs["pk"]}))




    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            data = super().get_mixin_context(super().get_context_data(unathorized=True))
            return self.render_to_response(context=data)


        pk = str(kwargs["pk"])
        from_page = request.GET.get("from")




        sentence = Sentence.objects.filter(id=pk)
        if sentence.count() == 0:
            return redirect("home")

        data_sent = sentence[0].data[0]




        change_sentence_data = request.user.change_sentence.get(pk) if request.user.change_sentence else None


        tokens = data_sent["tokens"]

        if change_sentence_data and change_sentence_data.get("tokens") is not None:
            if change_sentence_data and len(change_sentence_data.get("tokens")) != len(tokens):
                print("ERROR", len(change_sentence_data.get("tokens")), len(tokens))
            if change_sentence_data and change_sentence_data.get("tokens") is not None:
                for i, text_token in enumerate(change_sentence_data.get("tokens")):
                    if i < len(tokens):
                        tokens[i]["text"] = text_token



        question_list = sum([p["question_list"] for p in data_sent["simple_sentences_in"]], [])
        questions_txt_list = []

        for f,t,q in question_list:
            questions_txt_list.append(words2questions(tokens[f]["text"], tokens[t]["text"], q))

        if change_sentence_data and change_sentence_data.get("lined") is not None:
            data = [{"type": word} for word in change_sentence_data.get("lined")]
        else:
            data = [{"type": word["line"]} for word in tokens]
            lined = [ word["line"] for word in tokens]

            if not request.user.change_sentence:
                request.user.change_sentence = {pk:{"lined":lined, "question_list":question_list,"questions_txt_list":questions_txt_list, "tokens":[w["text"] for w in tokens] }}

            elif not request.user.change_sentence.get(pk):
                request.user.change_sentence[pk] = {"lined": lined, "question_list": question_list, "questions_txt_list":questions_txt_list, "tokens":[w["text"] for w in tokens] }
            request.user.save()


        formset = WordFormSet(initial=data)
        # questions_list = data_sent["question_list"] # Parent_to_children.objects.values_list('question', flat=True).distinct()
        question_form = RelationForm()  # questions=question_list)

        data = super().get_mixin_context(super().get_context_data(
            formset=formset,
            question_form=question_form,
            list_forms=zip(formset, tokens),
            questions=question_list,
            questions_txt=questions_txt_list,
            sent_id=pk,
            send_form=SendForm(),
            form_remove=RemoveForm(),
            back=from_page,
            form_text_token=TextTokenForm()
        ))

        return self.render_to_response(context=data)




class SaveSentence(BaseMixin, TemplateView):
    template_name = "index.html"


    def post(self, request, **kwargs):
        pk = str(self.kwargs["pk"])
        if not request.user.is_authenticated:
            print("unath")
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk":pk }))

        form_send = SendForm(request.POST)
        if not form_send.is_valid():
            print(form_send.errors)
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))




        changed = request.user.change_sentence

        if not changed or not changed.get(pk):
            print("404")
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))
        changed_sent = changed.get(pk)

        if request.user.verified:
            sentence = Sentence.objects.filter(id=pk)
            if len(sentence) == 0:
                return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))
            sentence = sentence[0]

            question_list = changed_sent.get("question_list")

            lined = form_send.cleaned_data["lines"].split()
            tokens = changed_sent.get("tokens")
            print(tokens)


            # lined

            id_part = 0
            id_t = 0
            for token, line, token_txt in zip(sentence.data[0]["tokens"], lined, tokens):
                token["line"] = line
                if id_t > len(sentence.data[0]["simple_sentences_in"][id_part]) -1:
                    id_part+=1
                    if id_part >= len(sentence.data[0]["simple_sentences_in"]):
                        break
                sentence.data[0]["simple_sentences_in"][id_part]["tokens"][id_t]["line"] = line
                sentence.data[0]["simple_sentences_in"][id_part]["tokens"][id_t]["text"] = token_txt
                id_t+=1


            # Question list
            sentence.data[0]["question_list"] = question_list


            sentence.verified = True
            sentence.save()

            #media delete

            # clear user

            request.user.change_sentence.pop(pk)
            request.user.save()
            print(request.user.change_sentence)
        return HttpResponseRedirect(reverse("sentence", kwargs={"pk": pk}))


def remove_sentence(request, pk):
    pk = str(pk)
    if (request.method != "POST" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

    form = RemoveForm(request.POST)
    if not form.is_valid():
        print(form.errors)
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))
    id_remove = form.cleaned_data["id_remove"]




    if id_remove >= len(request.user.change_sentence[pk]["question_list"]) or id_remove < 0:
        print("redirect")
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))
    request.user.change_sentence[pk]["question_list"].pop(id_remove)

    request.user.save()
    return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))


def edit_token_text(request, pk, token_id_0):
    pk = str(pk)
    if (request.method != "GET" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))
    new_value = request.GET.get("value")
    if new_value =="":
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))
    if request.user.change_sentence[pk].get("tokens") is None:
        data=Sentence.objects.filter(id=pk)[0].data[0]["tokens"]
        request.user.change_sentence[pk]["tokens"] = [t["text"] for t in data]

    request.user.change_sentence[pk]["tokens"][int(token_id_0)] = new_value
    request.user.save()
    return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))






