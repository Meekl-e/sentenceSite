from django import forms


class TaskForm(forms.Form):
    date_expired = forms.DateTimeField(required=False, )
