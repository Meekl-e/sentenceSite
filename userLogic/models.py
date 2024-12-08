from django.contrib.auth.models import AbstractUser
from django.db import models


#
# class Student2Teacher(models.Model):
#     student = IntegerField()
#     teacher = IntegerField()

class CorrectUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Ученик'),
        ('teacher', 'Учитель'),
    ]
    id = models.IntegerField(primary_key=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=False)
    first_name = models.CharField(max_length=120, blank=False)
    school = models.CharField(max_length=120, blank=False)
    s_class = models.CharField(max_length=120, blank=False)
    city = models.CharField(max_length=120, blank=False)
    last_name = models.CharField(max_length=120, blank=False)
    second_last_name = models.CharField(max_length=120, blank=True, null=True)
    verified = models.BooleanField(default=False)
    change_sentence = models.JSONField(blank=True,null=True, default=None)
    teacher_students = models.ManyToManyField("userLogic.CorrectUser", related_name="students")
    student_invite = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.second_last_name} {self.last_name}"
