import re

import nltk
import pymorphy3
import requests
import spacy
from natasha import NewsEmbedding, Segmenter, NewsSyntaxParser, Doc, NewsMorphTagger
from ufal.udpipe import Model, Pipeline

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

nltk.download('punkt')
nltk.download('punkt_tab')
print("Loanding NLTK completed")


class SentenceDefault:
    text = str()
    question_list = list()
    tokens = list()
    name = str()

    type_goal = "Повествовательное"
    type_intonation = "Невосклицательное"
    gram_bases = "Простое"
    main_members = "Двусоставное"
    second_members = "Нераспространенное"
    lost_members = "Полное"
    difficulty_members = "Неосложнённое"
    schem = ""




    def __init__(self, text, tokens, question_list, name):
        """
        Text - предложение
        question_list - список вопросов формата (id_from, id_to, question)
        tokens - список токенов
        url - путь к изображению
        tokens_list - ключи к предложению
        name - название нейросети
        """
        self.text = text
        self.question_list = question_list
        self.tokens = tokens

        #self.tokens.sort(key=lambda x:x.id)
        self.name = name

    def __dict__(self):
        return {
            "name": self.name,
            "question_list": self.question_list,
            "tokens": [t.__dict__() for t in self.tokens],
            "type_goal": self.type_goal,
            "type_intonation": self.type_intonation,
            "gram_bases": self.gram_bases,
            "main_members": self.main_members,
            "second_members": self.second_members,
            "lost_members": self.lost_members,
            "difficulty_members": self.difficulty_members,
            "schem": self.schem
        }

    def __len__(self):
        return len(self.text)

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return (all(f1==f2 and t1==t2 and q1==q2 for (f1,t1,q1), (f2,t2,q2)  in zip(self.question_list, other.question_list))
                and all(s == o for s, o in zip(self.tokens,  other.tokens)))


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
            return self.text + "\n" + ("_" * len(self.text))
        if self.line == "double_line":
            return self.text + "\n" + ("=" * len(self.text))
        if self.line == "dotted_line":
            return self.text + "\n" + ("_ " * (len(self.text) // 2))
        if self.line == "dotted_circle_line":
            return self.text + "\n" + ("_." * (len(self.text) // 2))
        if self.line == "wavy_line":
            return self.text + "\n" + (r"\/" * (len(self.text) // 2))
        if self.line == "circle":
            return self.text + "\n" + (r"()" * (len(self.text) // 2))

    def __repr__(self):
        return f"{self.id}-{self.text}-{self.line}-{self.pos}".lower()

    def __dict__(self):
        return {
            "id_in_sentence": self.id,
            "text": self.text,
            "line": self.line,
            "pos": self.pos,
        }


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
        "X": ""
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


def sentence_tokenize(text) -> list:
    return nltk.tokenize.sent_tokenize(text, "russian")


def analysis_spacy(text) -> SentenceDefault:
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
                                       token_first.children))

            minus += 2
            adding = False
            tokens_map[token.i] = token.i - minus
            tokens_map[token.i - 1] = token.i - minus + 1
        elif token.text == "-":
            if text.find(tokens[-1].text + " -") == -1:
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
    # print(question_list, tokens, "SPACY")
    return analysis_full(SentenceDefault(text, tokens, question_list, "Spacy"))


def analysis_natasha(text) -> SentenceDefault:
    doc = Doc(text)
    doc.segment(segmenter)
    doc.parse_syntax(syntax_parser)
    doc.tag_morph(tagger)

    question_list = []
    tokens = []

    for token in doc.tokens:

        head_id = int(token.head_id.split("_")[-1]) - 1
        id = int(token.id.split("_")[-1]) - 1

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

    # print(question_list, tokens, "NATASHA")
    return analysis_full(SentenceDefault(text, tokens, question_list, "Natasha"))


def analysis_UDPipe(text) -> SentenceDefault:
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
            text, id, translate_dep_to_line(dep), pos
        ))
        if head_id != 0:
            question = translate_to_question(dep)
            if question != " ":
                question_list.append((id, head_id, question))

    # print(question_list, tokens, "UDPipe")

    return analysis_full(SentenceDefault(text, tokens, question_list, "UDPipe"))


def analysis_full(sentence) -> SentenceDefault:
    grammars_line = 0
    grammars_double_line = 0
    punctuation = 0
    soyz = 0
    find_1per_npro = False
    find_3per_npro = False

    if sentence.tokens[-1].text == "!":
        sentence.type_intonation = "Восклицательное"

    if sentence.tokens[-1].text == "?":
        sentence.type_goal = "Вопросительное"

    chance_max = -1
    for idx, token in enumerate(sentence.tokens):
        # token = TokenDefault()
        print(token.text)
        parsed = morph.parse(token.text)[0]

        if parsed.tag.POS == "NPRO" and parsed.tag.person in ["1per", "2per"] and parsed.tag.case == "nomn":
            find_1per_npro = True
            if sentence.main_members == "Односоставное определенно-личное":
                sentence.main_members = ""

        if parsed.tag.POS == "NPRO" and parsed.tag.person == "3per" and parsed.tag.case == "nomn":
            find_3per_npro = True
            if sentence.main_members == "Односоставное неопределенно-личное":
                sentence.main_members = ""

        procent = parsed.score

        if not parsed.tag.mood is None and parsed.tag.mood == "impr" and chance_max < procent:  # повелит. наклон
            sentence.type_goal = f"Побудительное |вероятность: {round(procent * 100)}%"
            chance_max = procent

        if not find_1per_npro and parsed.tag.POS == "VERB" and parsed.tag.mood in ["indc",
                                                                                   "impr"] and parsed.tag.person in [
            "1per", "2per"] and parsed.tag.tense == "pres":
            sentence.main_members = "Односоставное определенно-личное"

        if not find_3per_npro and parsed.tag.POS == "VERB" and parsed.tag.mood in ["indc",
                                                                                   "impr"] and parsed.tag.person in [
            "1per", "2per"] and parsed.tag.tense == "pres":
            sentence.main_members = "Односоставное неопределенно-личное"

        if not find_3per_npro and parsed.tag.POS == "VERB" and parsed.tag.mood in ["indc",
                                                                                   "impr"] and parsed.tag.person in [
            "1per", "2per"] and parsed.tag.tense == "pres":
            sentence.main_members = "Односоставное неопределенно-личное"

        if token.line not in ["double_line", "line"]:
            sentence.second_members = "Распространённое"
        elif token.line == "double_line":
            grammars_double_line += 1
        elif token.line == "line":
            grammars_line += 1

        if token.pos == "":
            punctuation += 1

        if parsed.tag.POS == "CONJ":
            soyz += 1

        if token.text == "-":
            print("Find --")
            if not ((idx != 0 and sentence.tokens[idx - 1].line == "line") and (
                    idx != len(sentence.tokens) and sentence.tokens[idx + 1].text == "это")):
                if not (("double_line" in sentence.tokens[:idx] and "line" in sentence.tokens[:idx]) and (
                        "double_line" in sentence.tokens[idx + 1:] and "line" in sentence.tokens[idx + 1:])):
                    if sentence.lost_members.lower() == "полное":  # не изменяли
                        sentence.lost_members = f"Неполное |Обнаружен пропущенный(ые) член(ы) предложения на месте №{idx}"
                    else:
                        sentence.lost_members += f", {idx}"

    if grammars_line == 1 == grammars_double_line:
        sentence.gram_bases = "Простое"
    if (grammars_double_line > 1 and grammars_line > 1) and punctuation > 1:
        sentence.gram_bases = f"Сложное ({min(grammars_line, grammars_double_line)} ГО) |Будьте аккуратны! Алгоритм плохо рассчитывает односоставные предложения"

    if grammars_line > 1 and grammars_double_line - grammars_line <= 0:
        sentence.difficulty_members = "Осложнено однородными подлежащими |Будьте осторожны! Подлежащее может являться назывной односоставной частью!"

    if grammars_line - grammars_double_line <= 0 and grammars_double_line > 1:
        sentence.difficulty_members = "Осложнено однородными сказуемыми |Будьте осторожны! Сказуемое может являться безличной односоставной частью!"

    return sentence


print(morph.parse("стихало")[0].tag)
print(morph.parse("шумело")[0].tag)






def parsing(text=""):
    """Подавать только очищенный текст"""
    result = []

    spacy_res = analysis_spacy(text)
    natasha_res = analysis_natasha(text)
    udpipe_res = analysis_UDPipe(text)

    if spacy_res == natasha_res == udpipe_res:
        result = [spacy_res]
    elif spacy_res == natasha_res or udpipe_res==natasha_res:
        result = [spacy_res, udpipe_res]
    elif spacy_res == udpipe_res:
        result = [spacy_res, natasha_res]
    else:
        result = [spacy_res, udpipe_res, natasha_res]
    return result


