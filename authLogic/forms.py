from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from userLogic.models import CorrectUser


class RegisterFrom(UserCreationForm):
    first_name = forms.CharField(label="Имя",
                                 widget=forms.TextInput(
                                     attrs={"class": "form-control", "id": "first_name",
                                            "placeholder": "Введите имя"}))
    username = forms.CharField(label="Логин (отображаемое имя)",
                                 widget=forms.TextInput(
                                     attrs={"class": "form-control", "id": "username",
                                            "placeholder": "Логин (отображаемое имя)"}))
    last_name = forms.CharField(label="Фамилия",
                                widget=forms.TextInput(
                                    attrs={"class": "form-control", "id": "last_name",
                                           "placeholder": "Введите фамилию"}))
    email = forms.EmailField(label="Почта",
                             widget=forms.EmailInput(
                                 attrs={ "type":"email", "class":"form-control", "id":"email", "placeholder":"name@example.com"}))
    birth = forms.DateField(label="Ваша дата рождения", required=False,
                            widget=forms.DateInput(attrs={"type":"date", "id":"birth", "style":"font:Georgia" }))

    password1 = forms.CharField(label="Пароль",
                               widget=forms.PasswordInput(
                                   attrs={"type": "password", "class": "form-control", "id": "password1",
                                          "placeholder": "Введите пароль"}))
    password2 = forms.CharField(label="Повторите пароль",
                               widget=forms.PasswordInput(
                                   attrs={"type": "password", "class": "form-control", "id": "password2",
                                          "placeholder": "Повторите пароль"}))
    role = forms.ChoiceField(required=False, label="Ваша роль", widget=forms.Select( attrs={"class": "form-select", "id":"role",
                                                                                  "aria-label":""},),
        choices=(("student", "Ученик"), ("teacher", "Учитель")))
    class Meta:
        model = CorrectUser
        fields = ('username','first_name', 'last_name', 'email', 'birth', 'password1', 'password2', 'role')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин",
                                 widget=forms.TextInput(
                                     attrs={"class": "form-control", "id": "username",
                                            "placeholder": "Введите логин", "style":"background-color: #4ac1f7; "}))
    password = forms.CharField(label="Пароль",
                                 widget=forms.PasswordInput(
                                     attrs={"type":"password", "class": "form-control ", "id": "password",
                                            "placeholder": "Введите пароль", "style":"background-color: #4ac1f7; "}))





