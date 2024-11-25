from pprint import pprint

from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView

from analysSentenceLogic.models import Sentence
from utils import BaseMixin
from .forms import *


def words2questions(w_from, w_to, question) -> str:
    if question.lower() != "очп":
        return w_from + f" == {question.capitalize()} ==> " + w_to
    else:
        return f"{w_from}, {w_to} - Однородные члены предложения"

class ChangeSentence(BaseMixin, TemplateView):
    template_name = "change_sentence.html"

    def post(self, request, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": kwargs["pk"]}))

        kwargs["pk"] = str(kwargs["pk"])


        formset = WordFormSet(request.POST)

        question_form = RelationForm(data=request.POST)


        if not formset.is_valid() or not question_form.is_valid():
            print(formset)
            print("Formset", formset.errors)
            print("Question", question_form.errors)
            print( question_form.is_valid())
            data = super().get_mixin_context(super().get_context_data(formset=formset, question_form=question_form))
            data["sent_id"] = kwargs["pk"]
            return self.render_to_response(context=data)

        try:
            from_i, to_i = map(int, question_form.cleaned_data["selected"].split("-"))
        except Exception as e:
            print(e, "error")
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": kwargs["pk"]}))


        lined = [form.cleaned_data["type"] for form in formset]
        question = question_form.cleaned_data["question"]




        if not request.user.change_sentence:
            request.user.change_sentence = {}


        if not request.user.change_sentence.get(kwargs["pk"]):
            request.user.change_sentence[kwargs["pk"]] = {}

        if not request.user.change_sentence[kwargs["pk"]].get("question_list"):
            request.user.change_sentence[kwargs["pk"]]["question_list"] = []



        append = True

        for f, t, q in request.user.change_sentence[kwargs["pk"]]["question_list"]:
            if f == from_i and t == to_i and q.lower()==question.lower():
                append = False

        if append:
            for i in range(len(request.user.change_sentence[kwargs["pk"]]["question_list"])):
                o = request.user.change_sentence[kwargs["pk"]]["question_list"][i]
                if o[0] == from_i and o[1] == to_i:
                    request.user.change_sentence[kwargs["pk"]]["question_list"].pop(i)

                    request.user.save()
                    break

        request.user.change_sentence[kwargs["pk"]]["lined"] = lined
        if append:

            request.user.change_sentence[kwargs["pk"]]["question_list"].append((from_i, to_i, question.capitalize()))

        print(request.user.change_sentence[kwargs["pk"]])
        print(1)


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

        tokens = data_sent.get("tokens")

        if change_sentence_data and change_sentence_data.get("tokens") is not None:
            tokens.clear()
            for i, (text_token, l, p) in enumerate(
                    zip(change_sentence_data.get("tokens"), change_sentence_data.get("lined"),
                        change_sentence_data.get("pos"))):
                tokens.append({
                    "id_in_sentence": i,
                    "line": l,
                    "pos": p,
                    "text": text_token
                })

        if not change_sentence_data:
            question_list = sum([p["question_list"] for p in data_sent["simple_sentences_in"]], [])

        elif change_sentence_data.get("question_list") is None:
            question_list = sum([p["question_list"] for p in data_sent["simple_sentences_in"]], [])

        else:
            question_list = change_sentence_data.get("question_list")


        questions_txt_list = []

        for f,t,q in question_list:
            questions_txt_list.append(words2questions(tokens[f]["text"], tokens[t]["text"], q))

        if change_sentence_data and change_sentence_data.get("lined") is not None:
            data = [{"type": word} for word in change_sentence_data.get("lined")]
        else:
            data = [{"type": word["line"]} for word in tokens]

        if not change_sentence_data:
            lined = [ word["line"] for word in tokens]
            pos = [word["pos"] for word in tokens]

            if not request.user.change_sentence:
                request.user.change_sentence = {}

            schema = data_sent["schema"]
            schema_cor = []
            for line, word in schema:
                if word not in "[]()":
                    schema_cor.append(line)

            request.user.change_sentence[pk] = {"lined": lined, "question_list": question_list,
                                                "tokens": [w["text"] for w in tokens],
                                                "pos": pos, "parts": data_sent.get("simple_sentences_in"),
                                                "gram_bases": data_sent["gram_bases"],
                                                "type_goal": data_sent["type_goal"],
                                                "type_intonation": data_sent["type_intonation"],
                                                "schema": schema_cor}

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
            form_remove=RemoveForm(),
            back=from_page,
        ))

        return self.render_to_response(context=data)





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
        print("redirect", len(request.user.change_sentence[pk]["question_list"]), id_remove)
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

    request.user.change_sentence[pk]["tokens"][int(token_id_0)] = new_value

    request.user.save()
    return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))


def edit_pos_text(request, pk, token_id_0):
    pk = str(pk)
    if (request.method != "GET" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))
    new_value = request.GET.get("value")
    if new_value == "":
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

    request.user.change_sentence[pk]["pos"][int(token_id_0)] = new_value

    request.user.save()
    return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))


def remove_token(request, pk, token_id_0):
    pk = str(pk)

    if (request.method != "GET" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

    sentence = Sentence.objects.filter(pk=pk)
    if len(sentence) == 0:
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

    data = request.user.change_sentence[pk]
    data["tokens"].pop(token_id_0)
    data["lined"].pop(token_id_0)
    data["pos"].pop(token_id_0)
    data["schema"].pop(token_id_0)
    new_questions = []
    for f, t, q in data["question_list"]:
        if f == token_id_0 or t == token_id_0:
            continue
        if f > token_id_0:
            f -= 1
        if t > token_id_0:
            t -= 1
        new_questions.append((f, t, q))
    data["question_list"] = new_questions

    change = False
    for p in data["parts"]:
        idx = 0
        for t in p["tokens"]:
            print(change, t)
            if change:
                t["id_in_sentence"] -= 1
            if t["id_in_sentence"] == token_id_0 - 1 and change is False:
                p["tokens"].pop(idx + 1)
                change = True
            idx += 1

    pprint(data["parts"])


    request.user.save()
    return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))


def add_token(request, pk, token_id):
    pk = str(pk)

    if (request.method != "GET" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

    sentence = Sentence.objects.filter(pk=pk)
    if len(sentence) == 0:
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

    data = request.user.change_sentence[pk]

    data["tokens"].insert(token_id, "измените текст")
    data["lined"].insert(token_id, "none")
    data["pos"].insert(token_id, "без ЧР")
    data["pos"].insert(token_id, "без ЧР")
    data["schema"].insert(token_id, "none")
    new_questions = []
    for f, t, q in data["question_list"]:
        if f >= token_id:
            f += 1
        if t >= token_id:
            t += 1
        new_questions.append((f, t, q))
    data["question_list"] = new_questions

    change = False
    for p in data["parts"]:
        idx = 0
        for t in p["tokens"]:
            if change:
                t["id_in_sentence"] += 1
            if t["id_in_sentence"] == token_id and change is False:
                p["tokens"].insert(idx, {
                    "id_in_sentence": token_id,
                    "text": "измените текст",
                    "line": "none",
                    "pos": "без ЧР"
                })
                change = True
            idx += 1

    pprint(data["parts"])


    request.user.save()
    return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))


def edit_line(request, pk, token_id_0):
    pk = str(pk)

    if (request.method != "GET" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

    sentence = Sentence.objects.filter(pk=pk)
    if len(sentence) == 0:
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

    new_value = request.GET.get("value")
    if new_value == "":
        return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

    request.user.change_sentence[pk]["lined"][int(token_id_0)] = new_value

    request.user.save()
    return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))





