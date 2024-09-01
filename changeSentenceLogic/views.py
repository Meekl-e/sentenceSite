from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from analysSentenceLogic.sentParsing.creating_image import draw, getDefaultParametrs

from utils import BaseMixin
from .forms import *
from analysSentenceLogic.models import Sentence, Parent_to_children

def draw_realtion(token_from, token_to,question, width):
    params = getDefaultParametrs()
    params["name"] = token_from + " " + token_to
    params["width"] = width

    return draw(token_from + " " + token_to, [" ", " "], [(0, 1, question)],
               params)

class ChangeSentence(BaseMixin, TemplateView):
    template_name = "change_sentence.html"

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": kwargs["pk"]}))

        kwargs["pk"] = str(kwargs["pk"])
        print(request.POST)
        formset = WordFormSet(request.POST)

        question_form = RelationForm(data=request.POST)


        if not formset.is_valid() or not question_form.is_valid():
            print("Formset errors:", formset.errors)
            print("Question form errors:", question_form.errors)
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

        if not request.user.change_sentence[kwargs["pk"]].get("media_list"):
            request.user.change_sentence[kwargs["pk"]]["media_list"] = []

        append = True

        for f, t, q in request.user.change_sentence[kwargs["pk"]]["question_list"]:
            if f == from_i and t == to_i and q.lower()==question.lower():
                append = False

        if append:
            for i in range(len(request.user.change_sentence[kwargs["pk"]]["question_list"])):
                o = request.user.change_sentence[kwargs["pk"]]["question_list"][i]
                if o[0] == from_i and o[1] == to_i:
                    request.user.change_sentence[kwargs["pk"]]["question_list"].pop(i)
                    src = request.user.change_sentence[kwargs["pk"]]["media_list"].pop(i)
                    fs.delete(src.removeprefix("/media/"))
                    #request.user.save()
                    break

        request.user.change_sentence[kwargs["pk"]]["lined"] = lined
        if append:
            token_from, token_to = tokens[from_i], tokens[to_i]
            src = draw_realtion(token_from, token_to, question, question_form.cleaned_data["width"] // 2)
            print(src)
            request.user.change_sentence[kwargs["pk"]]["question_list"].append((from_i, to_i, question.capitalize()))
            request.user.change_sentence[kwargs["pk"]]["media_list"].append(src)




        request.user.save()
        print(request.user.change_sentence)

        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": kwargs["pk"]}))




    def get(self, request, **kwargs):
        if not request.user.is_authenticated:
            data = super().get_mixin_context(super().get_context_data(unathorized=True))
            return self.render_to_response(context=data)


        pk = str(kwargs["pk"])
        tokens = self.get_tokens(pk)
        if tokens is None:
            return redirect("home")

        change_sentence_data = request.user.change_sentence.get(pk) if request.user.change_sentence else None

        media_list = []
        question_list = []
        if change_sentence_data and change_sentence_data.get("lined") is not None:
            data = [{"type": word} for word in change_sentence_data.get("lined")]
            if change_sentence_data.get("media_list"):
                media_list = change_sentence_data.get("media_list")
        else:
            data = [{"type": word.line} for word in tokens]
            lined = [ word.line for word in tokens]
            for object_question in Parent_to_children.objects.filter(sentence_id=int(pk)):
                f = object_question.parent_id
                t = object_question.child_id
                q = object_question.question
                question_list.append((f,t,q))
                src = draw_realtion(tokens[f].text, tokens[t].text, q, 300)
                media_list.append(src)
            if not request.user.change_sentence:
                request.user.change_sentence = {pk:{"lined":lined, "question_list":question_list, "media_list":media_list}}

            elif not request.user.change_sentence.get(pk):
                request.user.change_sentence[pk] = {"lined": lined, "question_list": question_list, "media_list": media_list}
            request.user.save()


        formset = WordFormSet(initial=data)
        questions_list = Parent_to_children.objects.values_list('question', flat=True).distinct()
        question_form = RelationForm(questions=questions_list)
        data = super().get_mixin_context(super().get_context_data(
            formset=formset,
            question_form=question_form,
            list_forms=zip(formset, tokens),
            rendered=media_list,
            sent_id=pk,
            send_form=SendForm(),
            form_remove=RemoveForm()
        ))

        return self.render_to_response(context=data)

    def get_tokens(self, pk):
        tokens = Sentence.objects.filter(id=pk)
        if tokens.count() == 0:
            return None
        tokens = tokens[0].tokens.all()
        return tokens


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
                print("pk not")
                return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))
            sentence = sentence[0]

            question_list = changed_sent.get("question_list")
            media_list= changed_sent.get("media_list")
            lined = form_send.cleaned_data["lines"].split()
            print(lined)


            # lined
            for token, line in zip(sentence.tokens.all(), lined):
                token.line = line
                token.save()

            # Question list
            Parent_to_children.objects.filter(sentence_id=pk).delete()
            for f,t,q in question_list:
                Parent_to_children.objects.create(
                    sentence_id=pk,
                    parent_id=f,
                    child_id=t,
                    question=q,
                )

            # image
            params = getDefaultParametrs()
            params["name"] = sentence.text.lower()
            src = draw(sentence.text, lined, question_list,params )
            sentence.image = src
            sentence.verified = True
            sentence.save()

            #media delete
            for file in media_list:
                fs.delete(file.removeprefix("/media/"))

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




    if id_remove >= len(request.user.change_sentence[pk]["media_list"]) or id_remove < 0:
        print("redirect")
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))
    src = request.user.change_sentence[pk]["media_list"].pop(id_remove)
    request.user.change_sentence[pk]["question_list"].pop(id_remove)

    fs.delete(src.removeprefix("/media/"))
    request.user.save()
    return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))



fs = FileSystemStorage()