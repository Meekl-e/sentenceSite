import random

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView

from analysSentenceLogic.models import Sentence
from studentTasksLogic.models import TaskSentences
from teacherTasksLogic.models import Task
from utils import BaseMixin


class TaskView(BaseMixin, TemplateView):
    template_name = "tasks.html"

    def get_context_data(self, id_task, **kwargs):
        data = self.get_mixin_context(super().get_context_data())
        if not self.request.user.is_authenticated:
            return data
        task = Task.objects.filter(id=id_task)
        if len(task) == 0:
            print("ee")
            return data
        task = task[0]
        if (self.request.user not in task.students_to.all()):
            print("eee")
            return data

        data["pars_result"] = task.sentences.all()
        data["id_task"] = task.id
        data["from_request"] = reverse("task", kwargs={"id_task": task.id})
        sents = TaskSentences.objects.filter(user=self.request.user.id, task=id_task)
        data["already_sentences"] = [(s.sentence_data, s.sentence) for s in sents]

        return data


@login_required
def sent_task(request, sent_id, id_task):
    student = request.user
    sent = Sentence.objects.filter(id=sent_id)
    if len(sent) == 0:
        return HttpResponseRedirect(reverse("student_page"))
    sent = sent[0]
    tokens = sent.data[0]["tokens"]
    l_tokens = len(tokens)

    parts = [{
        "question_list": [],
        "tokens": [],
        "main_members": random.choice(["Двусоставное", "Односоставное"]),
        "second_members": random.choice(["Распространённое", "Нераспространённое"]),
        "lost_members": random.choice(["Полное", "Неполное"]),
        "difficulty_members": "Неосложнённое",
        "type_part": "Сочинительная часть"

    }]

    for i, t in enumerate(tokens):
        print(t)
        parts[0]["tokens"].append({
            "id_in_sentence": i,
            "text": t["text"],
            "line": "none",
            "pos": "напишите часть речи",
            "type": "напишите тип члена предложения",
        })

    student.change_sentence[sent_id] = {
        "lined": ["none"] * l_tokens, "question_list": [],
        "tokens": [w["text"] for w in tokens],
        "pos": ["напишите часть речи"] * l_tokens, "parts": parts,
        "gram_bases": random.choice(["Простое", "Сложное"]),
        "type_goal": random.choice(["Повествовательное", "Побудительное", "Вопросительное"]),
        "type_intonation": random.choice(["Восклицательное", "Невосклицательное"]),
        "schema": ["none"] * l_tokens, "type": ["напишите тип члена предложения"] * l_tokens,
        "task": id_task,
    }
    student.save()
    print(student.change_sentence)
    return HttpResponseRedirect(reverse("change_sentence", kwargs={"pk": sent_id}))
