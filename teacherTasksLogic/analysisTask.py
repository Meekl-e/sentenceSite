from pprint import pprint

from pydantic.v1.schema import schema

from analysSentenceLogic.sentParsing.parser import SentenceDefault
from studentTasksLogic.models import StudentTask
from teacherTasksLogic.models import Task
from collections import Counter


def compare(original, student):
    data = {"Ошибка в определении цели предложения": False, "Ошибка в определении интонации предложения": False,
            "Ошибка в делении предложения на простое/сложное": False}
    count = 0
    for e_o, e in zip(["type_goal", "type_intonation", "gram_bases"], data.keys()):
        if original[e_o] != student[e_o]:
            data[e] = False
            count += 1

    schema_orig = Counter([i[0] for i in original["schema"]])
    schema_student = Counter([i[0] for i in student["schema"]])

    if schema_orig.get("none"):
        schema_orig["word"] += schema_orig["none"]
        schema_orig.pop("none")
    if schema_student.get("none"):
        schema_student["word"] += schema_student["none"]
        schema_student.pop("none")

    schema_orig.subtract(schema_student)

    data["Ошибки в схеме предложения"] = 0
    for v in schema_orig.values():
        data["Ошибки в схеме предложения"] += abs(v)
    data["Ошибки в схеме предложения"] //= 2
    count += data["Ошибки в схеме предложения"]

    pos = []
    type = []
    line = []
    text = []
    for tok in original["tokens"]:
        if len(tok["pos"]) >= 3:
            if tok["pos"].startswith("нап"):
                pos.append(" ")
            else:
                pos.append(tok["pos"][:3].lower())
        else:
            pos.append(tok["pos"].lower())

        if len(tok["type"]) >= 3:
            if tok["type"].startswith("нап"):
                type.append(" ")
            else:
                type.append(tok["type"][:3].lower())
        else:
            type.append(tok["type"].lower())
        line.append(tok["line"].lower())
        text.append(tok["text"].lower())

    pos_s = []
    type_s = []
    line_s = []
    text_s = []
    for tok in student["tokens"]:
        if len(tok["pos"]) >= 3:
            if tok["pos"].startswith("нап"):
                pos_s.append(" ")
            else:
                pos_s.append(tok["pos"][:3].lower())
        else:
            pos_s.append(tok["pos"].lower())

        if len(tok["type"]) >= 3:
            if tok["type"].startswith("нап"):
                type_s.append(" ")
            else:
                type_s.append(tok["type"][:3].lower())
        else:
            type_s.append(tok["type"].lower())
        line_s.append(tok["line"].lower())
        text_s.append(tok["text"].lower())

    pos = Counter(pos)
    type = Counter(type)
    line = Counter(line)
    text = Counter(text)

    pos_s = Counter(pos_s)
    type_s = Counter(type_s)
    line_s = Counter(line_s)
    text_s = Counter(text_s)

    if line.get("none"):
        line["word"] += line["none"]
        line.pop("none")
    if line_s.get("none"):
        line_s["word"] += line_s["none"]
        line_s.pop("none")

    pos.subtract(pos_s)
    type.subtract(type_s)
    line.subtract(line_s)
    text.subtract(text_s)

    print(pos)
    print(type)
    print(line)
    print(text)

    data["Ошибки в определении частей речи"] = 0
    data["Ошибки в определении типа члена предложения"] = 0
    data["Ошибки с подчеркиванием членов предложения"] = 0
    data["Ошибки в словах/Неправильных запятых"] = 0

    for k in pos.keys():
        v = abs(pos[k])
        data["Ошибки в определении частей речи"] += v
    data["Ошибки в определении частей речи"] //= 2
    count += data["Ошибки в определении частей речи"]

    for k in type.keys():
        v = abs(type[k])
        data["Ошибки в определении типа члена предложения"] += v
    data["Ошибки в определении типа члена предложения"] //= 2
    count += data["Ошибки в определении типа члена предложения"]

    for k in line.keys():
        v = abs(line[k])
        data["Ошибки с подчеркиванием членов предложения"] += v
    data["Ошибки с подчеркиванием членов предложения"] //= 2
    count += data["Ошибки с подчеркиванием членов предложения"]

    for k in text.keys():
        v = abs(text[k])
        data["Ошибки в словах/Неправильных запятых"] += v
    data["Ошибки в словах/Неправильных запятых"] //= 2
    count += data["Ошибки в словах/Неправильных запятых"]

    if len(original["simple_sentences_in"]) != len(student["simple_sentences_in"]):
        data["Разбивка на части"] = "Ошибка"
        count += 1
    else:
        for i, (p, p_student) in enumerate(zip(original["simple_sentences_in"], student["simple_sentences_in"])):

            start = min(p["tokens"], key=lambda x: x["id_in_sentence"])['id_in_sentence']
            end = max(p["tokens"], key=lambda x: x["id_in_sentence"])['id_in_sentence']
            start_s = min(p_student["tokens"], key=lambda x: x["id_in_sentence"])['id_in_sentence']
            end_s = max(p_student["tokens"], key=lambda x: x["id_in_sentence"])['id_in_sentence']
            if p["main_members"] != p_student["main_members"]:
                data["Двусоставное/Односоставное"] = "Ошибка"
                count += 1
            if p["second_members"] != p_student["second_members"]:
                data["Распространенное/Нераспространенное"] = "Ошибка"
                count += 1
            if p["second_members"] != p_student["second_members"]:
                data["Распространенное/Нераспространенное"] = "Ошибка"
                count += 1
            if p["lost_members"] != p_student["lost_members"]:
                data["Полное/Неполное"] = "Ошибка"
                count += 1
            if p["difficulty_members"] != p_student["difficulty_members"]:
                data["Неосложненное/Осложненное"] = "Ошибка"
                count += 1
            if start != start_s or end != end_s:
                data["Разбивка на части"] = "Ошибка"
                count += 1

    data["Всего ошибок"] = count
    pprint(data)
    return data


def analisysTask(result=StudentTask):
    user = result.user
    task_id = result.task
    sentences = result.sentences.all()
    result.result_check = []
    data = result.result_check
    sent_task = Task.objects.filter(id=task_id)
    if len(sent_task) == 0:
        return None
    sent_task = sent_task[0].sentences
    for s in sentences:
        for s_correct in sent_task.all():
            if s.sentence == s_correct.id:
                data.append(compare(s_correct.data[0], s.sentence_data))
                break

    result.save()
