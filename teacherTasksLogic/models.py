from datetime import datetime

from django.db import models

from analysSentenceLogic.models import Sentence


class Task(models.Model):
    sentences = models.ManyToManyField(to="analysSentenceLogic.sentence", related_name="sentences_task")
    teacher_id = models.IntegerField(blank=False)
    students_to = models.ManyToManyField(to="userLogic.correctuser", related_name="students_task")
    students_passed = models.ManyToManyField(to="userLogic.correctuser", related_name="students_pass")
    date = models.DateField(auto_now_add=True, blank=False)
    date_expired = models.DateField(default=datetime.fromisoformat("2099-12-31"))
    check_phrases = models.BooleanField(null=False, default=False)
    remove_punctuation = models.BooleanField(null=False, default=True)
    apply = models.BooleanField(blank=False, default=False)

    def __str__(self):
        if len(self.sentences.all()) > 0:
            s = self.sentences.all()[0]
            return s.text
        else:
            return "Задание"
