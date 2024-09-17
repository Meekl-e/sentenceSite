import spacy
import requests
import re
import pymorphy3

from natasha import NewsEmbedding, Segmenter, NewsSyntaxParser, Doc, NewsMorphTagger
from ufal.udpipe import Model, Pipeline

from . import creating_image

nlp = spacy.load("ru_core_news_lg")
print("Loading Spacy completed")

emb = NewsEmbedding()
segmenter = Segmenter()
syntax_parser = NewsSyntaxParser(emb)
tagger = NewsMorphTagger(emb)
print("Loading Natasha completed")

model = Model.load("analysSentenceLogic/sentParsing/models/russian-syntagrus-ud-2.5-191206.udpipe")
pipeline = Pipeline(model, 'tokenize', Pipeline.DEFAULT, Pipeline.DEFAULT, 'conllu')
print("Loading UDPipe completed")

morph = pymorphy3.MorphAnalyzer()
print("Loading pymorphy3 completed")

class SentenceDefault:
    text = str()
    question_list=list()
    tokens = list()
    url = str()

    def __init__(self, text, question_list, tokens, url):
        """
        Text - предложение
        question_list - список вопросов формата (id_from, id_to, question)
        tokens - список токенов
        url - путь к изображению
        tokens_list - ключи к предложению
        """
        self.text = text
        self.question_list = question_list
        self.tokens = tokens
        self.url = url

    def __len__(self):
        return len(self.text)
    def __str__(self):
        return self.text

class TokenDefault:
    def __init__(self, text, id, line, pos, children=None):

        self.text = text
        self.id = id
        self.children = children
        self.line = line
        self.pos = translate_pos(pos)
        self.type = None

    def __len__(self):
        return len(self.text)
    def __str__(self):
        if self.line == "line":
            return self.text+"\n"+("_"*len(self.text))
        if self.line == "double_line":
            return self.text+"\n"+("="*len(self.text))
        if self.line == "dotted_line":
            return self.text+"\n"+("_ "*(len(self.text)//2))
        if self.line == "dotted_circle_line":
            return self.text+"\n"+("_."*(len(self.text)//2))
        if self.line == "wavy_line":
            return self.text+"\n"+(r"\/"*(len(self.text)//2))
        if self.line == "circle":
            return self.text+"\n"+(r"()"*(len(self.text)//2))

    def __repr__(self):
        return f"{self.id}-{self.text}-{self.line}-{self.pos}"

def translate_to_question(dep):
    dep = dep.lower()
    question_map = {
        "nsubj": "Что?",
        "obj": "Что?",
        "obl": "Где?",
        "advmod": "Как?",
        "amod": "Какой?",
        "nmod": "Чей?",
        "det": "Какой?",
        "cc": "И?",
        "mark": "Как?",
        "aux": "Что?",
        "cop": "Что?",
        "parataxis": "Что?"
    }
    return question_map.get(dep, " ")


def translate_dep_to_line(dep):
    dep = dep.lower()
    dep_map = {
        "root": "double_line",
        "conj": "double_line",
        "amod": "wavy_line",
        "det": "wavy_line",
        "nmod": "dotted_line",
        "obj": "dotted_line",
        "obl": "dotted_line",
        "nsubj": "line",
        "cc": "circle",
        "advmod": "dotted_circle_line",
        "mark": "dotted_circle_line",
        "cop": "line",
        "aux": "line",
        "parataxis": "dotted_circle_line"
    }

    return dep_map.get(dep, "none")

def translate_pos(pos):
    pos = pos.upper()
    pos_map = {
        "ADJ": "Прилагательное",
        "ADP": "Предлог",
        "ADV": "Наречие",
        "AUX": "Глагол-связка",
        "CCONJ": 'Сочинительный союз',
        "DET": "Артикль",
        "INTJ": "Междометие",
        "NOUN": 'Существительное',
        "NUM": "Числительное",
        "PART": "Частица",
        "PRON": "Местоимение",
        "PROPN": "Имя собственное",
        "PUNCT": "",
        "SCONJ": "Подчинительный союз",
        "SYM": "Символ",
        "VERB": "Глагол",
        "X": "..."
    }
    return pos_map.get(pos, " ")

def clear_text(text=str()):
    text = re.sub(pattern=r" {2,}", repl=" ", string=text)
    api_url = "https://speller.yandex.net/services/spellservice.json/checkText"
    params = {"text": text, "lang": "ru"}

    try:
        response = requests.get(api_url, params=params)
        response.raise_for_status()
        suggestions = response.json()
        sugs = []
        for e in suggestions:
            text = text.replace(e["word"], e["s"][0])
            sugs.append((e["word"], e["s"][0]))
    except requests.RequestException as e:
        print("TooLarge")
    return text

def analysis_spacy(text):
    doc = nlp(text)

    question_list = []
    tokens = []

    tokens_map = {}
    minus = 0

    adding = False
    for token in doc:
        if adding:
            token_first = tokens.pop(-1)


            tokens.append(TokenDefault(token_first.text + "-" + token.text,
                                       token_first.id,
                                       token_first.line, token_first.pos,
                                       token_first.children ))

            minus +=2
            adding = False
            tokens_map[token.i] = token.i - minus
            tokens_map[token.i-1] = token.i - minus +1
        elif token.text == "-":
            if text.find(tokens[-1].text+" -") == -1:
                adding = True
        else:
            tokens_map[token.i] = token.i - minus
            tokens.append(TokenDefault(token.text, tokens_map[token.i], translate_dep_to_line(token.dep_),
                                       token.pos_, token.children))



    for token in tokens:

        for child in token.children:
            q = translate_to_question(child.dep_)
            if q != " ":
                question_list.append((token.id, tokens_map[child.i], translate_to_question(child.dep_)))
    print(question_list, tokens, "SPACY")
    return tokens, question_list


def analysis_natasha(text):
    doc = Doc(text)
    doc.segment(segmenter)
    doc.parse_syntax(syntax_parser)
    doc.tag_morph(tagger)

    question_list = []
    tokens = []


    for token in doc.tokens:


        head_id = int(token.head_id.split("_")[-1])-1
        id = int(token.id.split("_")[-1]) -1
        print([token])
        tokens.append(TokenDefault(token.text,
                                   id,
                                   translate_dep_to_line(token.rel),
                                   token.pos))

        if head_id == -1:
            continue
        rel = token.rel
        q = translate_to_question(rel)
        if q != " ":
            question_list.append((head_id, id, q))

    print( question_list, tokens, "NATASHA")
    return  tokens, question_list

def analysis_UDPipe(text):

    processed = pipeline.process(text)

    tokens = []
    question_list = []

    for line in processed.split("\n"):
        if line.startswith("#") or len(line) == 0:
            continue


        token_parsed = line.split("\t")

        id = int(token_parsed[0])
        text = token_parsed[1]
        dep = token_parsed[7]
        head_id = int(token_parsed[6])
        pos = token_parsed[3]


        tokens.append(TokenDefault(
            text,id, translate_dep_to_line(dep),pos
        ))
        if head_id != 0:
            question = translate_to_question(dep)
            if question != " ":
                question_list.append((id, head_id, question))


    print(question_list, tokens, "UDPipe")
    return  tokens, question_list


def parsing(text=""):
    """Подавать только очищенный текст"""

    spacy_res = analysis_spacy(text)
    natasha_res = analysis_natasha(text)

    udpipe_res = analysis_UDPipe(text)

    if spacy_res[0] != natasha_res[0]:
        print("Разные результаты")
        print(spacy_res[0], "spacy")
        print(natasha_res[0], "natasha")

    if spacy_res[0] != udpipe_res[0]:
        print("Разные результаты")
        print(spacy_res[0], "spacy")
        print(udpipe_res[0], "udpipe_res")

    if natasha_res[0] != udpipe_res[0]:
        print("Разные результаты")
        print(natasha_res[0], "natahsa")
        print(udpipe_res[0], "udpipe_res")

    """
    lst_ress = []
    for tokens, questions in [spacy_res, udpipe_res,natasha_res]:
        lst_ress.append(SentenceDefault(text, questions, tokens,
                           draw_res(tokens, questions)))
    return lst_ress
    """
    return SentenceDefault(text, udpipe_res[1], udpipe_res[0],
                           None)



    """
    parameters = creating_image.getDefaultParametrs()
    parameters["name"] = text.replace(" ", "_")
    print(text, lined, question_list)
    url = creating_image.draw(token_teksts, lined, question_list, parameters)
    print(url)
    return SentenceDefault(text, lined, question_list, tokens, url)  # displacy.render(doc, style='dep', jupyter=False), doc
    """