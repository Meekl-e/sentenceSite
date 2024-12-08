from django import forms
from django.forms import HiddenInput


class TaskForm(forms.Form):
    date_expired = forms.DateTimeField(required=False, )


class RemoveTaskForm(forms.Form):
    task_id = forms.CharField(max_length=20, required=True, widget=HiddenInput())
