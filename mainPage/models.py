from django.contrib.auth.models import AbstractUser
from django.db import models


class Sentence(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=3000, blank=False)
    len = models.IntegerField(blank=False)
    date = models.DateTimeField(auto_now_add=True, blank=False)
    tokens = models.JSONField(blank=False)
    count = models.IntegerField(blank=False, default=1)

    def __str__(self):
        return self.text


class Token(models.Model):
    id = models.IntegerField(primary_key=True)
    id_in_sentence = models.IntegerField(blank=False)
    text = models.CharField(max_length=3000, blank=False)
    head_text = models.CharField(max_length=3000, blank=False)
    len = models.IntegerField(blank=False)
    head_id = models.IntegerField(blank=True)
    pos = models.CharField(max_length=10, blank=False)
    dep = models.CharField(max_length=10, blank=False, default="none")
    children = models.JSONField()

    def __str__(self):
        return self.text