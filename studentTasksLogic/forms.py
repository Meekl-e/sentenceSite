from django import forms


class SentTaskForm(forms.Form):
    task_id = forms.IntegerField(required=True, widget=forms.HiddenInput())
