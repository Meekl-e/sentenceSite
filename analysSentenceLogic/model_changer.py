from django.core.files.storage import FileSystemStorage

from analysSentenceLogic.models import *

from analysSentenceLogic.sentParsing.parser import SentenceDefault

"""
Sentence.objects.all().delete()
Token.objects.all().delete()
Parent_to_children.objects.all().delete()
"""


def create_sentence(sentences=None):
    if sentences is None:
        sentences = [SentenceDefault]

    if Sentence.objects.all().count() >= MAX_OBJECTS:
        o = Sentence.objects.order_by("date", "-count").first()
        o.delete()


    json_values = []

    for result in sentences:
        json_values.append(result.__dict__())
    print(json_values)

    sent = Sentence.objects.create(
        len=len(sentences[0]),
        text=str(sentences[0]),
        data=json_values
        # image=sentence.url
    )

    #
    # for token in sentence.tokens:
    #     tokenModel, created = Token.objects.get_or_create(
    #         len=len(token),
    #         text=token.text,
    #         pos=token.pos,
    #         line=token.line,
    #         id_in_sentence=token.id,
    #     )
    #     print(tokenModel.id)
    #     sent.tokens.add(tokenModel)
    #
    # for id_from, id_to, question in sentence.question_list:
    #
    #     relation = Parent_to_children.objects.create(
    #         sentence_id=sent.id,
    #         parent_id=id_from,
    #         child_id=id_to,
    #         question=question
    #     )
    #
    # sent.save()
    return sent.id

fs = FileSystemStorage()