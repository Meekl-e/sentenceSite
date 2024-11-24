from django.http import HttpResponseRedirect
from django.urls import reverse

from analysSentenceLogic.models import Sentence
from analysSentenceLogic.sentParsing.parser import text2clear_text


def save_sentence(request, pk, ):
    pk = str(pk)
    if (request.method != "GET" or
            not request.user.is_authenticated or
            not request.user.change_sentence.get(pk)):
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))

    changed = request.user.change_sentence

    if not changed or not changed.get(pk):
        print("404")
        return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))
    changed_sent = changed.get(pk)

    if request.user.verified:
        sentence = Sentence.objects.filter(id=pk)
        if len(sentence) == 0:
            return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))
        sentence = sentence[0]

        if ['gram_bases', 'lined', 'parts', 'pos', 'question_list', 'schema', 'tokens', 'type_goal',
            'type_intonation'] != sorted(list(changed_sent.keys())):
            print("NOT COR USER")
            return HttpResponseRedirect(reverse("change_parts", kwargs={"pk": pk}))

        lined = changed_sent.get("lined")
        tokens = changed_sent.get("tokens")
        pos = changed_sent.get("pos")
        parts = changed_sent.get("parts")

        # lined

        id_t = 0

        tokens_all = []

        for line, token_txt, p in zip(lined, tokens, pos):
            tokens_all.append({
                "id_in_sentence": id_t,
                "text": token_txt,
                "line": line,
                "pos": p
            })
            id_t += 1

        schema = changed_sent.get("schema")

        i = 0
        schema_all = []
        for p in parts:

            last_id = max(p["tokens"], key=lambda x: x["id_in_sentence"])
            first_id = min(p["tokens"], key=lambda x: x["id_in_sentence"])
            for t in p["tokens"]:
                if t == first_id:
                    if p["type_part"] == "Сочинительная часть":
                        schema_all.append(("word", "["))
                    if p["type_part"] == "Подчинительная часть":
                        schema_all.append(("word", "("))

                if t == last_id:
                    if p["type_part"] == "Сочинительная часть":
                        schema_all.append(("word", "]"))
                    if p["type_part"] == "Подчинительная часть":
                        schema_all.append(("word", ")"))
                schema_all.append((schema[i], tokens_all[i]["text"]))

                i += 1

        sentence.data.clear()

        sentence.data.append({
            "name": "verified",
            "type_goal": changed_sent.get("type_goal"),
            "type_intonation": changed_sent.get("type_intonation"),
            "gram_bases": changed_sent.get("gram_bases"),
            "simple_sentences_in": parts,
            "tokens": tokens_all,
            "schema": schema_all
        })

        # sentence.data[0]["tokens"].clear()
        # sentence.data[0]["simple_sentences_in"].clear()
        # sentence.data[0]["simple_sentences_in"].append({
        #     "question_list": question_list,
        #     "tokens": [],
        #     "main_members": "Двусоставное",
        #     "second_members": "Распространённое",
        #     "lost_members": "Полное",
        #     "difficulty_members": "Неосложнённое"
        # })
        # print(lined)
        #
        # print(sentence.data[0]["simple_sentences_in"])
        # print(sentence.data[0]["tokens"])

        # Question list
        # sentence.data[0]["question_list"] = question_list
        sentence.text = " ".join(tokens)
        sentence.text_clear, _ = text2clear_text("".join(tokens))

        # sentence.data = [sentence.data[0]]

        sentence.verified = True
        sentence.save()

        # media delete

        # clear user

        request.user.change_sentence.pop(pk)
        request.user.save()
        print(request.user.change_sentence)
    return HttpResponseRedirect(reverse("sentence", kwargs={"pk": pk}))
