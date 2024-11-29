from django.contrib.auth.models import AbstractUser
from django.db import models

class CorrectUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Ученик'),
        ('teacher', 'Учитель'),
    ]
    id = models.IntegerField(primary_key=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=False)
    birth_date = models.DateField(null=True, blank=True)
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=120, blank=False)
    last_name = models.CharField(max_length=120, blank=False)
    verified = models.BooleanField(default=True)
    change_sentence = models.JSONField(blank=True,null=True, default=None)
    teacher_students = models.ManyToManyField("userLogic.CorrectUser", related_name="students")
    student_invite = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"




