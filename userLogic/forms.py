from django import forms
from django.forms import HiddenInput


class AcceptInvitationForm(forms.Form):
    code = forms.CharField(max_length=20, required=True, widget=HiddenInput())
