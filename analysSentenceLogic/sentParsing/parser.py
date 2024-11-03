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
print("Loading NLTK completed")


class SentenceDefault:
    name = str()
    simple_sentences_in = []

    type_goal = "Повествовательное"
    type_intonation = "Невосклицательное"
    gram_bases = "Простое"

    def __init__(self, name, simple_sentence_in, tokens):
        """
        Обёртка для всех предложений.
        """
        self.simple_sentences_in = simple_sentence_in

        self.tokens = tokens

        self.name = name

        self.clear_text = re.sub(r"\W", "", "".join([t.text for t in self.tokens])).lower()

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

    def get_clear(self):
        return self.clear_text




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
        self.length = len(tokens)


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
        return f"|{self.text}|".lower()

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

        if len(self.text) == 1 and self.text.lower() !="я":
            self.line = "none"

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
        return self.text

    def __repr__(self):
        return f"{self.id}-{self.text}-{self.line}-{self.pos}".lower()

    def __eq__(self, other):
        return self.text.lower() == other.text.lower() and self.line == other.line and self.pos == other.pos and self.id == other.id

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
        "nsubj": " ",
        "obj": "Что?",
        "obl": "Где?",
        "advmod": "Как?",
        "amod": "Какой?",
        "nmod": "Чей?",
        "det": "Какой?",
        "cc": " ",
        "mark": "Как?",
        "aux": "Что?",
        "cop": "Что?",
        "parataxis": "Что?",
        "conj": "ОЧП",
        "advcl": "Что делая?",
        "xcomp":"Что?"

    }
    print(question_map.get(dep, " "))
    return question_map.get(dep, " ")


def translate_dep_to_line(dep, word):
    dep = dep.lower()
    dep_map = {
        "root": "double_line",
        "conj": "double_line",  # dotted_line
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
        "parataxis": "dotted_circle_line",
        "acl:relcl":"double_line",
        "appos":"wavy_line",
        "compound":"wavy_line",
        "advcl": "dotted_circle_line",
        "xcomp": "dotted_line"
    }
    res  = dep_map.get(dep, dep)#"none")
    if res in ["advcl"]:
        parsed = morph.parse(word)[0]
        if parsed.tag.POS == "VERB":
            return "double_line"
        else:
            return "dotted_circle_line"
    return res


def translate_pos(pos):
    pos = pos.upper()
    pos_map = {
        "ADJ": "Прилагательное",
        "ADP": "Предлог",
        "ADV": "Наречие",
        "AUX": "Глагол-связка",
        "CCONJ": 'Сочинительный союз',
        "DET": "Местоимение",
        "INTJ": "Междометие",
        "NOUN": 'Существительное',
        "NUM": "Числительное",
        "PART": "Частица",
        "PRON": "Местоимение",
        "PROPN": "Имя собственное",
        "PUNCT": " ",
        "SCONJ": "Подчинительный союз",
        "SYM": "",
        "VERB": "Глагол",
        "X": ""
    }
    return pos_map.get(pos, "")


def set_regexp(text=""):
    text = re.sub(r"[\n\t\r]", " ", text)

    text = re.sub(pattern=r'[«‹„❝❮「『‚“‘‛„‚]', repl='«', string=text)
    text = re.sub(pattern=r'[»›“❞❯」』‘”’’”’]', repl='»', string=text)
    text = re.sub(pattern=r'[`\"\']', repl='"', string=text)
    text = re.sub(pattern=r'\.\.\.', repl='…', string=text)
    text = re.sub(r'\"+', '"', text)

    text = re.sub(r"[^а-яА-Я\…\"\«\»\ \.\!\?\,\:\;\-\+\=\(\)\№\^\%\*\~\d]", " ", text, flags=re.IGNORECASE)
    text = re.sub(r";+",";", text)
    text = re.sub(r" +"," ", text)

    return text

def clear_text(text=str()):
    text=set_regexp(text)
    print(text)

    text = text[0].upper() + text[1:]

    sym = text[-1]
    if sym in ",:;":
        text = text[:-1] + "."
    elif not sym in "!.?…":
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


def text2clear_text(text=""):
    """Возвращает текст без пробелов и знаков препиния"""

    c_t = re.sub(r"\W", "", text).lower()
    no_sign_text = ""

    if "!" in text or "?" in text:
        for i, el in enumerate(text):
            if el == "!":
                c_t += "!"
                if i != 0 and not text[i - 1] in "?!":
                    no_sign_text += el
            elif el == "?":
                c_t += "?"
                if i != 0 and not text[i - 1] in "?!":
                    no_sign_text += el
            else:
                no_sign_text += el
    else:
        no_sign_text = text

    # print(c_t, no_sign_text)

    return c_t, no_sign_text



def sentence_tokenize(text) -> list:
    return nltk.tokenize.sent_tokenize(text, "russian")

def get_word_tokenize(res):

    res = set_regexp(res)
    return nltk.tokenize.word_tokenize(res, "russian")




def analysis_spacy(text, tokenized) -> [SentenceDefault]:
    doc = nlp(text)

    # displacy.serve(doc, style="dep")

    question_list = []
    tokens = []

    tokens_map = {}
    minus = 0

    adding = False
    for token in doc:
        # if translate_dep_to_line(token.dep_, token.text) == token.dep_:
        # print(token.text, token.dep_, text[token.idx - 10: token.idx + 10])

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
        elif token.i != 0 and token.text == "-":

            if text[token.idx-1] != " ":
                adding = True

            else:
                tokens_map[token.i] = token.i - minus

                tokens.append(TokenDefault(token.text, tokens_map[token.i], translate_dep_to_line(token.dep_, token.text),
                                           token.pos_, token.children))
        else:
            tokens_map[token.i] = token.i - minus
            tokens.append(TokenDefault(token.text, tokens_map[token.i], translate_dep_to_line(token.dep_, token.text),
                                       token.pos_, token.children))
    # print(tokens_map)
    for token in tokens:

        for child in token.children:
            q = translate_to_question(child.dep_)
            if q != " ":
                question_list.append((token.id, tokens_map[child.i], translate_to_question(child.dep_)))
    # print(question_list, tokens, "SPACY")
    return analysis_full(PartSentence(text, tokens, question_list, "Spacy")), PartSentence(text, tokens, question_list,
                                                                                           "Sp").tokens


def analysis_natasha(text, tokenized) -> [SentenceDefault]:
    doc = Doc(text)
    doc.segment(segmenter)
    doc.parse_syntax(syntax_parser)
    doc.tag_morph(tagger)

    # doc.sents[0].syntax.print()


    question_list = []
    tokens = []

    append = False
    head_first_id = 0
    rel_first = ""
    all_text_tokens = ""
    minus= 0
    all_ids = 0


    for id, token in enumerate(doc.tokens):

        head_id = int(token.head_id.split("_")[-1]) -1 + all_ids


        if id < len(doc.tokens)-1 and int(doc.tokens[id+1].id.split("_")[-1]) == 1:
            all_ids= id + 1

        if append:
            all_text_tokens+=token.text
            if all_text_tokens == tokenized[id-minus]:
                tokens.append(TokenDefault(all_text_tokens,
                                           id - minus,
                                           translate_dep_to_line(rel_first, all_text_tokens),
                                           token.pos))
                if head_first_id != -1:
                    q = translate_to_question(rel_first)
                    if q != " ":
                        question_list.append((head_first_id, id - minus, q))
                append = False
                all_text_tokens = ""

            continue


        if token.text != tokenized[id - minus]:
            print(token.text, tokenized[id - minus], )
            append = True
            head_first_id = head_id
            rel_first = token.rel
            all_text_tokens+=token.text
            minus+=1
            continue

        tokens.append(TokenDefault(token.text,
                                   id - minus,
                                   translate_dep_to_line(token.rel, token.text),
                                   token.pos))

        if head_id == all_ids -1:
            continue
        rel = token.rel
        q = translate_to_question(rel)
        if q != " ":
            question_list.append((head_id, id - minus, q))

    if all_text_tokens != "":
        tokens.append(TokenDefault(all_text_tokens,
                                   id - minus,
                                   translate_dep_to_line(rel_first, all_text_tokens),
                                   token.pos))
        if head_first_id != -1:
            q = translate_to_question(rel_first)
            if q != " ":
                question_list.append((head_first_id, id - minus, q))

    # print(question_list, tokens, "NATASHA")
    return analysis_full(PartSentence(text, tokens, question_list, "Natasha")), PartSentence(text, tokens,
                                                                                             question_list, "N").tokens


def analysis_UDPipe(all_text, tokenized) -> [SentenceDefault]:
    processed = pipeline.process(all_text)

    tokens = []
    question_list = []

    lines = processed.split("\n")

    tokens_map = {}
    minus = 0
    min_tokenize=0

    adding = False
    id_token_start = 0

    wait_for_token = False
    all_token_text = ""
    count_wait = 0

    for idx, line in enumerate(lines):

        if line.startswith("#") or len(line) == 0:
            min_tokenize+=1
            continue

        token_parsed = line.split("\t")

        id =  idx - min_tokenize #int(token_parsed[0]) - 1
        text = token_parsed[1]
        dep = token_parsed[7]
        pos = token_parsed[3]

        # print(id)
        if wait_for_token:
            all_token_text += text
            # print(all_token_text, tokenized[id-minus])
            if all_token_text == tokenized[id - minus]:

                wait_for_token = False
                for c in range(count_wait):
                    tokens_map[id - c] = id - minus
                tokens.append(TokenDefault(all_token_text,
                                           tokens_map[id],
                                           translate_dep_to_line(dep, all_token_text), pos))
                count_wait = 0
            else:
                minus += 1
                count_wait += 1

            continue

        if text != tokenized[id - minus]:

            if text[0] != "«" and text[-1] != "»" :
                wait_for_token = True
                all_token_text = text
                count_wait += 1
                minus += 1
                id_token_start += len(text)
                if not token_parsed[-1].startswith("SpaceAfter=No"):
                    id_token_start += 1
                continue
            elif text[1:] != tokenized[id - minus]:
                if text[-1] == "»":
                    if text[1:-1] != tokenized[id - minus]:
                        wait_for_token = True
                        all_token_text = text
                        count_wait += 1
                        minus += 1
                        id_token_start += len(text)
                        if not token_parsed[-1].startswith("SpaceAfter=No"):
                            id_token_start += 1
                        continue
                else:
                    wait_for_token = True
                    all_token_text = text
                    count_wait += 1
                    minus += 1
                    id_token_start += len(text)
                    if not token_parsed[-1].startswith("SpaceAfter=No"):
                        id_token_start += 1
                    continue

        if adding:
            token_first = tokens.pop(-1)
            tokens.append(TokenDefault(token_first.text + "-" + text,
                                       token_first.id,
                                       token_first.line, token_first.pos))

            minus += 2
            adding = False
            tokens_map[id] = id - minus
            tokens_map[id - 1] = id - minus + 1
        elif id != 0 and text == "-":
            print(all_text[id_token_start -3: id_token_start + 3], [all_text[id_token_start -1]], "r")
            if all_text[id_token_start -1] != " ":
                adding = True
            else:
                tokens_map[id] = id - minus
                tokens.append(TokenDefault(
                    text, tokens_map[id], translate_dep_to_line(dep,text), pos
                ))
        else:
            tokens_map[id] = id - minus
            if text[0] == "«":

                tokens.append(TokenDefault(
                "«", tokens_map[id], "", "OTHER"))
                minus -= 1
                min_tokenize+=1

                id += 1
                text = text[1:]

            tokens_map[id] =id - minus
            delete = False

            if text[-1] == "»":
                text = text[:-1]
                delete = True

            tokens.append(TokenDefault(
                text, tokens_map[id], translate_dep_to_line(dep, text), pos
            ))
            if delete:
                minus-=1
                min_tokenize+=1
                tokens_map[id+1] = id - minus
                tokens.append(TokenDefault(
                    "»", tokens_map[id], "", "OTHER"
                ))
        id_token_start += len(text)
        if not token_parsed[-1].startswith("SpaceAfter=No"):
            id_token_start+=1
    for idx, line in enumerate(lines):
        if line.startswith("#") or len(line) == 0:
            continue

        token_parsed = line.split("\t")

        id = int(token_parsed[0]) - 1
        # text = token_parsed[1]
        dep = token_parsed[7]
        head_id = int(token_parsed[6]) - 1



        if head_id != 0:
            question = translate_to_question(dep)
            if question != " ":
                question_list.append((tokens_map[head_id], tokens_map[id], question))

    # print(question_list, tokens, "UDPipe")

    return analysis_full(PartSentence(all_text, tokens, question_list, "UDPipe")), PartSentence(all_text, tokens,
                                                                                                question_list,
                                                                                                "UDPipe").tokens


def split_hard_sentence(sentence=PartSentence) -> [PartSentence]:
    candidates = [token for token in sentence.tokens if token.pos == " "]

    result = []

    used_tokens = []
    print("====")
    print(len(sentence.tokens))
    print(candidates, sentence.name)


    for idx, sep in enumerate(candidates):
        id_end = sep.id

        for id_start in range(idx - 1, -2, -1):
            if id_start != -1:
                id_start = candidates[id_start].id
            else:
                id_start = 0

            isSent = True
            lst_questions = []

            for f, t, q in sentence.question_list:
                if id_start < f < id_end:
                    if t > id_end or t < id_start:
                        # print(f, t, q, "question_break", id_start, id_end)
                        isSent = False
                        break
                    elif (f,t,q) not in lst_questions:
                        lst_questions.append((f, t, q))
                if id_start < t < id_end:
                    if f > id_end or f < id_start:
                        # print(f, t, q, "question_break", id_start, id_end, "2")
                        isSent = False
                        break
                    elif (f,t,q) not in lst_questions:
                        lst_questions.append((f, t, q))
            if isSent:
                append = True
                tokens_all = sentence.tokens[id_start:id_end + 1]
                # print(tokens_all)
                if id_start >= len(sentence.tokens) - 2:
                    append = False

                elif sentence.tokens[id_start + 1].pos in [" ", ""]:
                    append = False


                if append:
                    tokens = []
                    for t in tokens_all:
                        if t not in used_tokens:
                            tokens.append(t)
                            used_tokens.append(t)
                    if len(tokens) == 0 or (len(tokens) == 1 and tokens[0].pos in [" ", ""]):
                        continue

                    if tokens[0].pos in [" ", ""]:
                        tokens = tokens[1:]

                    for idx_used, p_used in enumerate(result):
                        break_find = False
                        for t in tokens:

                            if t in p_used.tokens:

                                if p_used.length < len(tokens):
                                    result.pop(idx_used)
                                    break_find = True
                                    break
                        if break_find:
                            break

                    sent_part = PartSentence(text=" ".join([i.text for i in tokens]), tokens=tokens, question_list=lst_questions, )

                    result.append(
                        sent_part
                    )
                break


    print(result)
    print("====")
    result.sort(key=lambda x: x.tokens[0].id)

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
        elif raspr is False and token.pos not in ["", " "]:
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


def analysis_full(sentence) -> SentenceDefault or None:
    if len(sentence.tokens) == 0:
        return None


    parts = split_hard_sentence(sentence)

    # print(parts, "parts")

    for part_sentence in parts:
        if analys_part_sentence(part_sentence):
            sentence.type_goal = "Побудительное"

    mainSentence = SentenceDefault(sentence.name, parts, sentence.tokens)

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
    tokenized = get_word_tokenize(text)

    spacy_res, sp = analysis_spacy(text, tokenized)
    # return [spacy_res]
    natasha_res, nat = analysis_natasha(text, tokenized)
    udpipe_res, ud = analysis_UDPipe(text, tokenized)

    m_tokens = len(max(spacy_res, natasha_res, udpipe_res, key=lambda x:len(x)))

    print(spacy_res.tokens)


    print(len(spacy_res), len(natasha_res), len(udpipe_res), len(tokenized))

    if spacy_res == natasha_res == udpipe_res:
        result = [spacy_res]
    elif spacy_res == natasha_res or udpipe_res == natasha_res:
        result = [spacy_res, udpipe_res]
    elif spacy_res == udpipe_res:
        result = [spacy_res, natasha_res]
    else:
        result = [spacy_res, udpipe_res, natasha_res]

    if len(spacy_res) < m_tokens:
        result.remove(spacy_res)
    if len(udpipe_res) < m_tokens:
        result.remove(udpipe_res)
    if len(natasha_res) < m_tokens:
        result.remove(natasha_res)

    return result
