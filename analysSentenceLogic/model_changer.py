from django.core.files.storage import FileSystemStorage

from analysSentenceLogic.models import *

from analysSentenceLogic.sentParsing.parser import SentenceDefault

"""
Sentence.objects.all().delete()
Token.objects.all().delete()
Parent_to_children.objects.all().delete()
"""


def create_sentence(sentence=SentenceDefault, type="Spacy"):
    if Sentence.objects.all().count() >= MAX_OBJECTS:
        o = Sentence.objects.order_by("date", "-count").first()

        all = Sentence_To_Token.objects.filter(sentence_id=o.id)

        tokens = Sentence_To_Token.objects.exclude(sentence_id=o.id)

        Parent_to_children.objects.filter(sentence_id=o.id).delete()

        for object in all:
            if tokens.filter(token_id=object.token_id).count() == 0:
                print(object.token_id, "DELETE")
                Token.objects.get(id=object.token_id).delete()
                object.delete()
        fs.delete(str(o.image).removeprefix("/media/"))
        o.delete()

    if type == "Spacy":

        sent = Sentence.objects.create(
            len=len(sentence),
            text=str(sentence),
            #image=sentence.url
        )



        for token in sentence.tokens:
            tokenModel, created = Token.objects.get_or_create(
                len=len(token),
                text=token.text,
                pos=token.pos,
                line=token.line,
                id_in_sentence=token.id,
            )
            print(tokenModel.id)
            sent.tokens.add(tokenModel)

        for id_from, id_to, question in sentence.question_list:

            relation = Parent_to_children.objects.create(
                sentence_id=sent.id,
                parent_id=id_from,
                child_id=id_to,
                question=question
            )

        sent.save()
    return sent.id

fs = FileSystemStorage()