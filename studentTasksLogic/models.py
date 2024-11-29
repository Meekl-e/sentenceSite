from django.db import models
from django.db.models import IntegerField, JSONField


class TaskSentences(models.Model):
    user = IntegerField(blank=False)
    task = IntegerField(blank=False)
    sentence = IntegerField(blank=False)
    sentence_data = JSONField(blank=False, default={})
