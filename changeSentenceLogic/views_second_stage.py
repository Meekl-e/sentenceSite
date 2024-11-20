from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from analysSentenceLogic.models import Sentence
from analysSentenceLogic.sentParsing.parser import text2clear_text
from utils import BaseMixin
from .forms import *


def words2questions(w_from, w_to, question) -> str:
    return w_from + f" == {question.capitalize()} ==> " + w_to


class ChangeParts(BaseMixin, TemplateView):
    template_name = "change_sentence_parts.html"

    def post(self, request, **kwargs):
        pk = str(kwargs["pk"])
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

        change_sentence_data = request.user.change_sentence.get(pk) if request.user.change_sentence else None

        if change_sentence_data is None:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

        request.user.save()

        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))

    def get(self, request, **kwargs):
        pk = str(kwargs["pk"])
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

        from_page = request.GET.get("from")

        change_sentence_data = request.user.change_sentence.get(pk) if request.user.change_sentence else None

        if change_sentence_data is None:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

        tokens = []
        for l, p, t in zip(change_sentence_data["lined"], change_sentence_data["pos"], change_sentence_data["tokens"]):
            tokens.append({"pos": p, "line": l, "text": t})

        # questions_list = data_sent["question_list"] # Parent_to_children.objects.values_list('question', flat=True).distinct()
        part_form = PartForm()  # questions=question_list)

        data = super().get_mixin_context(super().get_context_data(
            part_form=part_form,
            sent_id=pk,
            back=from_page,
            tokens=tokens,
        ))

        return self.render_to_response(context=data)


class SaveSentence(BaseMixin, TemplateView):
    template_name = "index.html"

    def post(self, request, **kwargs):
        pk = str(self.kwargs["pk"])
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

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

            if ['lined', 'pos', 'question_list', 'tokens'] != sorted(list(changed_sent.keys())):
                print("NOT COR USER")
                return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": pk}))

            question_list = changed_sent.get("question_list")
            lined = form_send.cleaned_data["lines"].split()
            tokens = changed_sent.get("tokens")
            pos = changed_sent.get("pos")
            print(tokens)

            # lined

            id_t = 0

            sentence.data[0]["tokens"].clear()
            sentence.data[0]["simple_sentences_in"].clear()
            sentence.data[0]["simple_sentences_in"].append({
                "question_list": question_list,
                "tokens": [],
                "main_members": "Двусоставное",
                "second_members": "Распространённое",
                "lost_members": "Полное",
                "difficulty_members": "Неосложнённое"
            })
            print(lined)
            for line, token_txt, p in zip(lined, tokens, pos):
                sentence.data[0]["simple_sentences_in"][0]["tokens"].append(
                    {
                        "id_in_sentence": id_t,
                        "line": line,
                        "text": token_txt,
                        "pos": p
                    }
                )
                sentence.data[0]["tokens"].append({
                    "id_in_sentence": id_t,
                    "text": token_txt,
                    "line": line,
                    "pos": p
                })
                id_t += 1
            print(sentence.data[0]["simple_sentences_in"])
            print(sentence.data[0]["tokens"])

            # Question list
            sentence.data[0]["question_list"] = question_list
            sentence.text = " ".join(tokens)
            sentence.text_clear, _ = text2clear_text("".join(tokens))

            sentence.data = [sentence.data[0]]

            sentence.verified = True
            sentence.save()

            # media delete

            # clear user

            request.user.change_sentence.pop(pk)
            request.user.save()
            print(request.user.change_sentence)
        return HttpResponseRedirect(reverse("sentence", kwargs={"pk": pk}))


def add_part(request, pk):
    pk = str(pk)
    if (request.method != "POST" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))

    return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))
