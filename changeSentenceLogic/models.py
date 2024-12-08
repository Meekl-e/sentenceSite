from django.db import models

from analysSentenceLogic.sentParsing.parser import model


class SentenceUnVerified(models.Model):
    text = models.CharField(max_length=100000, blank=False)
    text_clear = models.CharField(max_length=100000, blank=False)
    date = models.DateTimeField(auto_now_add=True, blank=False)
    sentence_id = models.IntegerField()
    changed_sentence = models.JSONField(blank=False, default=dict)

    data = models.JSONField(blank=False, default=dict)

    def __str__(self):
        return self.text
