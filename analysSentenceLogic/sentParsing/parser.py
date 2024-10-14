import re

import nltk
import pymorphy3
import requests
import spacy
from natasha import NewsEmbedding, Segmenter, NewsSyntaxParser, Doc, NewsMorphTagger
from ufal.udpipe import Model, Pipeline

nlp = spacy.load("ru_core_news_sm")
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
    name = str()
    simple_sentences_in = []

    type_goal = "Повествовательное"
    type_intonation = "Невосклицательное"
    gram_bases = "Простое"

    def __init__(self, name, simple_sentence_in):
        """
        Обёртка для всех предложений.
        """
        self.simple_sentences_in = simple_sentence_in

        self.tokens = []

        for part in simple_sentence_in:
            self.tokens += part.tokens

        self.name = name

    def __dict__(self):
        return {
            "name": self.name,
            "type_goal": self.type_goal,
            "type_intonation": self.type_intonation,
            "gram_bases": self.gram_bases,
            "simple_sentences_in": [i.__dict__() for i in self.simple_sentences_in],
            "tokens": [t.__dict__() for t in self.tokens]
        }

    def __len__(self):
        return len(self.tokens)

    def __repr__(self):
        return " ".join([t.text for t in self.tokens]).lower()

    def __str__(self):
        return " ".join([t.text for t in self.tokens]).lower()

    def __eq__(self, other):
        return all(s == o for s, o in zip(self.simple_sentences_in, other.simple_sentences_in))


class PartSentence:
    text = str()
    question_list = list()
    tokens = list()
    name = str()
    simple_sentences_in = []

    main_members = "Двусоставное"
    second_members = "Нераспространенное"
    lost_members = "Полное"
    difficulty_members = "Неосложнённое"

    def __init__(self, text, tokens, question_list, name=""):
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
        self.name = name

    def __dict__(self):
        return {
            "question_list": self.question_list,
            "tokens": [t.__dict__() for t in self.tokens],
            "main_members": self.main_members,
            "second_members": self.second_members,
            "lost_members": self.lost_members,
            "difficulty_members": self.difficulty_members,
        }

    def __len__(self):
        return len(self.text)

    def __repr__(self):
        return f"{self.text}".lower()

    def __str__(self):
        return self.text

    def __eq__(self, other):
        return (all(f1 == f2 and t1 == t2 and q1 == q2 for (f1, t1, q1), (f2, t2, q2) in
                    zip(self.question_list, other.question_list))
                and all(s == o for s, o in zip(self.tokens, other.tokens)))


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

    def __eq__(self, other):
        return self.text.lower() == other.text.lower() and self.line == other.line and self.pos == other.pos

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
    sym = text[-1]
    if not sym in "!.?":
        text += "."

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


def analysis_spacy(text) -> [SentenceDefault]:
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
        else:
            tokens_map[token.i] = token.i - minus
            tokens.append(TokenDefault(token.text, tokens_map[token.i], translate_dep_to_line(token.dep_),
                                       token.pos_, token.children))
    print(tokens_map)
    for token in tokens:

        for child in token.children:
            q = translate_to_question(child.dep_)
            if q != " ":
                question_list.append((token.id, tokens_map[child.i], translate_to_question(child.dep_)))
    print(question_list, tokens, "SPACY")
    return analysis_full(PartSentence(text, tokens, question_list, "Spacy"))


def analysis_natasha(text) -> [SentenceDefault]:
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

    print(question_list, tokens, "NATASHA")
    return analysis_full(PartSentence(text, tokens, question_list, "Natasha"))


def analysis_UDPipe(text) -> [SentenceDefault]:
    processed = pipeline.process(text)

    tokens = []
    question_list = []

    for line in processed.split("\n"):
        if line.startswith("#") or len(line) == 0:
            continue

        token_parsed = line.split("\t")

        id = int(token_parsed[0]) - 1
        text = token_parsed[1]
        dep = token_parsed[7]
        head_id = int(token_parsed[6]) - 1
        pos = token_parsed[3]

        tokens.append(TokenDefault(
            text, id, translate_dep_to_line(dep), pos
        ))
        if head_id != 0:
            question = translate_to_question(dep)
            if question != " ":
                question_list.append((head_id, id, question))

    print(question_list, tokens, "UDPipe")

    return analysis_full(PartSentence(text, tokens, question_list, "UDPipe"))


def split_hard_sentence(sentence=PartSentence) -> [PartSentence]:
    candidates = [token for token in sentence.tokens if token.pos == ""]
    result = []

    for idx, sep in enumerate(candidates):
        id_end = sep.id

        for id_start in range(idx - 1, -2, -1):
            if id_start != -1:
                id_start = candidates[id_start].id

            isSent = True
            lst_questions = []

            for f, t, q in sentence.question_list:
                if id_start <= f < id_end:
                    if t > id_end or t < id_start:
                        print(f, t, q, "question_break", id_start, id_end)
                        isSent = False
                        break
                    else:
                        lst_questions.append((f, t, q))
                elif id_start <= t < id_end:
                    if f > id_end or f < id_start:
                        print(f, t, q, "question_break", id_start, id_end, "2")
                        isSent = False
                        break
                    else:
                        lst_questions.append((f, t, q))
            if isSent:
                tokens = sentence.tokens[id_start + 1:id_end + 1]
                result.append(
                    PartSentence(text=" ".join([i.text for i in tokens]), tokens=tokens, question_list=lst_questions, )
                )
                break

    if len(result) == 0:
        return [sentence]
    else:
        return result


def analys_part_sentence(part_sentence) -> bool():
    count_p = 0
    count_sk = 0

    pobyditel = False

    raspr = False

    for idx, token in enumerate(part_sentence.tokens):
        if token.line == "line":

            count_p += 1
        elif token.line == "double_line":
            if idx != 0 and part_sentence.tokens[idx - 1].line != "double_line":
                count_sk += 1
        elif raspr is False:
            raspr = True
            part_sentence.second_members = "Распространённое"

    if count_p > 0 and count_sk > 0:
        one_main = False
    else:
        one_main = True
        if count_sk == 0:
            part_sentence.main_members = "Односоставное назывное"

    for idx, token in enumerate(part_sentence.tokens):
        # token = TokenDefault()

        if token.pos == "":
            if token.text == "-" and idx < len(part_sentence.tokens) - 1:
                print("Find --")
                if not ((idx != 0 and part_sentence.tokens[idx - 1].line == "line") and (
                        idx != len(part_sentence.tokens) - 1 and part_sentence.tokens[idx + 1].text == "это")):

                    if part_sentence.lost_members.lower() == "полное":  # не изменяли
                        part_sentence.lost_members = f"Неполное |Пропущенные члены на месте: {idx}"
                    else:
                        part_sentence.lost_members += f", {idx}"
                continue
            if token.text == ",":
                part_sentence.difficulty_members = "Осложнённое"

            continue

        parsed = morph.parse(token.text)[0]

        if not parsed.tag.mood is None and parsed.tag.mood == "impr":  # повелит. наклон
            pobyditel = True

        if one_main and token.line == "double_line":
            if (parsed.tag.POS == "VERB" and parsed.tag.mood in ["indc", "impr"]
                    and parsed.tag.person in ["1per", "2per"] and parsed.tag.tense == "pres"):
                part_sentence.main_members = "Односоставное определенно-личное"

            if (parsed.tag.POS == "VERB" and parsed.tag.mood in ["indc", "impr"]
                    and parsed.tag.person == "3per" and parsed.tag.tense in ["pres", "futr"]):
                part_sentence.main_members = "Односоставное неопределенно-личное"

            if (parsed.tag.POS == "VERB" and parsed.tag.tense in ["pres", "futr"]
                    and parsed.tag.person == "3per"
                    and parsed.tag.number == "sing"):
                part_sentence.main_members = "Односоставное безличное"

            if (parsed.tag.POS == "VERB" and parsed.tag.tense == "past"
                    and parsed.tag.number == "sing" and parsed.tag.gender == "neut"):
                part_sentence.main_members = "Односоставное безличное"
    return pobyditel


def analysis_full(sentence) -> SentenceDefault:
    parts = split_hard_sentence(sentence)

    print(parts, "parts")

    for part_sentence in parts:
        if analys_part_sentence(part_sentence):
            sentence.type_goal = "Побудительное"

    mainSentence = SentenceDefault(sentence.name, parts)

    if sentence.tokens[-1].text == "!":
        mainSentence.type_intonation = "Восклицательное"

    if sentence.tokens[-1].text == "?":
        mainSentence.type_goal = "Вопросительное"

    if len(parts) > 1:
        mainSentence.gram_bases = "Сложное"
    else:
        mainSentence.gram_bases = "Простое"

    return mainSentence


def parsing(text=""):
    """Подавать только очищенный текст"""

    spacy_res = analysis_spacy(text)
    natasha_res = analysis_natasha(text)
    udpipe_res = analysis_UDPipe(text)

    if spacy_res == natasha_res == udpipe_res:
        result = [spacy_res]
    elif spacy_res == natasha_res or udpipe_res == natasha_res:
        result = [spacy_res, udpipe_res]
    elif spacy_res == udpipe_res:
        result = [spacy_res, natasha_res]
    else:
        result = [spacy_res, udpipe_res, natasha_res]
    return result
