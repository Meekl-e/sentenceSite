from django.db import models
from django.db.models import IntegerField, JSONField


class TaskSentences(models.Model):
    user = IntegerField(blank=False)
    task = IntegerField(blank=False)
    sentence = IntegerField(blank=False)
    sentence_data = JSONField(blank=False)


class StudentTask(models.Model):
    user = IntegerField(blank=False)
    task = IntegerField(blank=False)
    sentences = models.ManyToManyField(TaskSentences, "sentences")
    result_check = models.JSONField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
