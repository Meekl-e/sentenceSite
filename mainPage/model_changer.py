from .models import *

def create_sentence(sentence, type="Spacy"):
    model = Sentence()
    if type == "Spacy":
        candidate = Sentence.objects.filter(text=str(sentence).lower())
        if len(candidate) >0:
            candidate[0].count +=1
            candidate[0].save()
            return
        model.len = len(sentence)
        model.text = str(sentence).lower()
        sp = []
        for token in sentence:
            candidate = Token.objects.filter(len=len(token),
                                             text=token.lower_,
                                             pos = token.pos_,
                                             head_text = token.head.lower_,
                                             dep = token.dep_,
                                             children = [t.i for t in token.children],
                                             head_id = token.head.i,
                                             id_in_sentence = token.i)
            if candidate:
                sp.append(candidate[0].id)
                continue
            tokenModel = Token()
            tokenModel.text = token.lower_
            tokenModel.len = len(token)
            tokenModel.pos = token.pos_
            tokenModel.head_id = token.head.i
            tokenModel.head_text = token.head.lower_
            tokenModel.id_in_sentence = token.i
            tokenModel.dep = token.dep_
            tokenModel.children = [t.i for t in token.children]
            tokenModel.save()
            sp.append(Token.objects.all().last().id)
        model.tokens = sp
        model.save()


