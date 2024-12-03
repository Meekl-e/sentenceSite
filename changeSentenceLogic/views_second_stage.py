from pprint import pprint

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from utils import BaseMixin
from .forms import *


def words2questions(w_from, w_to, question) -> str:
    return w_from + f" == {question.capitalize()} ==> " + w_to


class ChangeParts(BaseMixin, TemplateView):
    template_name = "change_sentence_parts.html"


    def get(self, request, **kwargs):
        pk = str(kwargs["pk"])
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

        from_page = request.GET.get("from")

        change_sentence_data = request.user.change_sentence.get(pk) if request.user.change_sentence else None

        if change_sentence_data is None:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

        tokens = []
        i = 0
        for l, p, t, ty in zip(change_sentence_data["lined"], change_sentence_data["pos"],
                               change_sentence_data["tokens"], change_sentence_data["type"]):
            tokens.append({"id_in_sentence": i, "pos": p, "line": l, "text": t, "type": ty})
            i += 1

        parts = change_sentence_data.get("parts")

        indexes = []

        for p in parts:
            sp = []
            for t in p["tokens"]:
                sp.append(tokens[t["id_in_sentence"]])
            if len(sp) == 0:
                parts.remove(p)
                continue
            p["tokens"] = sp

            last_id = max(p["tokens"], key=lambda x: x["id_in_sentence"])
            first_id = min(p["tokens"], key=lambda x: x["id_in_sentence"])

            for t in p["tokens"]:
                if t == first_id:
                    indexes.append((p["type_part"], "start"))
                elif t == last_id:
                    indexes.append((p["type_part"], "end"))
                else:
                    indexes.append(None)

        schema = [{"type_line": type} for type in change_sentence_data.get("schema")]







        # questions_list = data_sent["question_list"] # Parent_to_children.objects.values_list('question', flat=True).distinct()
        part_form = PartForm(initial=request.user.change_sentence[pk])  # questions=question_list)

        data = super().get_mixin_context(super().get_context_data(
            part_form=part_form,
            sent_id=pk,
            back=from_page,
            tokens=tokens,
            parts=zip(PartsFormSet(initial=parts), parts),
            schema=zip(SchemaFormSet(initial=schema), indexes, tokens),
            task=change_sentence_data.get("task")


        ))

        return self.render_to_response(context=data)


def add_part(request, pk):
    pk = str(pk)
    if (request.method != "POST" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))

    data = PartForm(request.POST)
    if not data.is_valid():
        print("Errors", data.errors)
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))

    tokens = request.user.change_sentence[pk].get("tokens")
    lined = request.user.change_sentence[pk].get("lined")
    pos = request.user.change_sentence[pk].get("pos")
    types = request.user.change_sentence[pk].get("type")

    if not tokens or not lined or not pos or not types:
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))

    f_part, t_part = map(int, data.cleaned_data["selected"].split("-"))

    f_part, t_part = min(f_part, t_part), max(f_part, t_part)
    t_part += 1

    txt_in_part = tokens[f_part:t_part]
    lines_in_part = lined[f_part:t_part]
    pos_in_part = pos[f_part:t_part]
    type_in_part = types[f_part:t_part]

    tokens_in_part = []
    for i, t, l, p, ty in zip(range(f_part, t_part), txt_in_part, lines_in_part, pos_in_part, type_in_part):
        tokens_in_part.append({
            "id_in_sentence": i,
            "text": t,
            "line": l,
            "pos": p,
            "type": ty,
        })

    parts = request.user.change_sentence[pk].get("parts")

    if parts is not None:
        for p in parts.copy():
            for token_other in p["tokens"].copy():
                if f_part <= token_other["id_in_sentence"] <= t_part:
                    p["tokens"].remove(token_other)
            if len(p["tokens"]) == 0:
                parts.remove(p)

    question_list = []
    for f, t, q in request.user.change_sentence[pk].get("question_list"):
        if f >= f_part and t <= t_part:
            question_list.append((f, t, q))

    data_sent = request.user.change_sentence[pk]
    if data_sent.get("parts") is None:
        data_sent["parts"] = []

    data_sent["parts"].append({
        "tokens": tokens_in_part,
        "question_list": question_list,

        "main_members": "Двусоставное",
        "second_members": "Распространённое",
        "lost_members": "Полное",
        "difficulty_members": "Неосложнённое",
        "type_part": data.cleaned_data["type"]

    })

    request.user.save()
    print(request.user.change_sentence[pk])

    return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))


def remove_part(request, pk, id):
    pk = str(pk)
    if (request.method != "GET" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))

    parts = request.user.change_sentence.get(pk).get("parts")
    if not parts:
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))

    if id < 0 or id >= len(parts):
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))

    print("delete suc")
    print(request.user.change_sentence[pk]["parts"].pop(id))
    request.user.save()
    return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))


def change_elem(request, pk, id_part, type):
    pk = str(pk)
    if (request.method != "GET" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))
    parts = request.user.change_sentence.get(pk).get("parts")
    if (id_part < 0 or id_part >= len(parts)) and type != "change_line":
        print("range")
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))
    print(id_part)

    if type in ["gram_bases", "type_goal", "type_intonation"]:
        value = request.GET.get("value")
        if type == "gram_bases" and value == "Простое":

            tokens_to_parts = []
            parts = request.user.change_sentence[pk]["parts"]
            for p in parts:
                tokens_to_parts = tokens_to_parts + p["tokens"]
            print(tokens_to_parts)
            parts[0]["tokens"] = tokens_to_parts
            request.user.change_sentence[pk]["parts"] = [parts[0]]

            print("change", request.user.change_sentence[pk]["parts"])
        if value and value != "":
            request.user.change_sentence[pk][type] = value
            request.user.save()

    elif type == "change_line":

        value = request.GET.get("value")
        if value and value != "":
            if id_part < len(request.user.change_sentence[pk]["schema"]):
                request.user.change_sentence[pk]["schema"][id_part] = value
                request.user.save()
    else:
        part_sent = parts[id_part]
        if part_sent.get(type) is None:
            print(type, "mme")
            return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))
        value = request.GET.get("value")
        if value and value != "":
            part_sent[type] = value
            request.user.save()

    print(request.user.change_sentence[pk]["parts"])
    return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))
