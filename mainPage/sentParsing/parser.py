import spacy
from spacy import displacy
import requests
import re

nlp = spacy.load("ru_core_news_lg")


def parsing (text=""):
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
        print(f"Error: {e}")
        return ""

    doc = nlp(text)
    return displacy.render(doc, style='dep', jupyter=False), doc
