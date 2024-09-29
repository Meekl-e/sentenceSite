from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm



class NameForm(forms.Form):

    text = forms.CharField(max_length=10000, required=True,
                           label="", widget=forms.Textarea(attrs={"rows":5, "cols":40,
                                                                  "class":'u-border-2 u-border-palette-5-dark-1 u-input u-input-rectangle u-radius u-input-3',
                                                                  'placeholder': 'Введите текст...'}),


                           error_messages={"required": "Введите ваше предложение, поле не должно быть пустым"},)



