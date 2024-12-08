from django.contrib.auth.models import AbstractUser
from django.db import models

MAX_OBJECTS = 1
#
# class Sentence_To_Token(models.Model):
#     sentence = models.ForeignKey('Sentence', on_delete=models.CASCADE)
#     token = models.ForeignKey("Token", on_delete=models.CASCADE)

class Parent_to_children(models.Model):
    sentence_id = models.IntegerField(blank=False)
    parent_id = models.IntegerField(blank=False)
    child_id = models.IntegerField(blank=False)
    question = models.CharField(blank=True, max_length=100)

    def __str__(self):
        return f"{self.parent_id} -{self.question}-> {self.child_id}."
#
# class Token(models.Model):
#     id_in_sentence = models.IntegerField(blank=False)
#     text = models.CharField(max_length=3000, blank=False)
#     len = models.IntegerField(blank=False)
#     pos = models.CharField(max_length=10, blank=False)
#     line = models.CharField(max_length=30, blank=False)
#
#     def __str__(self):
#         return self.text

class Sentence(models.Model):

    text = models.CharField(max_length=100000, blank=False)
    text_clear = models.CharField(max_length=100000, blank=False)
    len = models.IntegerField(blank=False)
    date = models.DateTimeField(auto_now_add=True, blank=False)
    # tokens = models.ManyToManyField(Token, blank=True,through="Sentence_To_Token")
    data = models.JSONField(blank=False, default=dict)
    count = models.IntegerField(blank=False, default=1)
    # image = models.CharField(blank=True, max_length=4000)
    verified = models.BooleanField(blank=False, default=False)
    likes = models.ManyToManyField("userLogic.CorrectUser", blank=True, related_name="likes")
    dislikes = models.ManyToManyField("userLogic.CorrectUser", blank=True, related_name="dislikes")
    favourites = models.ManyToManyField("userLogic.CorrectUser", blank=True, related_name="favourites")

    def __str__(self):
        return self.text



class RequestSentences(models.Model):

    id_request = models.CharField(max_length=50,  blank=False)
    request_sentences = models.ManyToManyField(to=Sentence, related_name="query_sentences")
    date = models.DateField(blank=False, auto_now_add=True)


    def __str__(self):
        return self.id_request


