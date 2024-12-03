from random import choices

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from userLogic.models import CorrectUser


class RegisterFrom(UserCreationForm):
    username = forms.CharField(label="",
                               widget=forms.TextInput(
                                   attrs={"class": "u-input u-input-rectangle", "id": "email",
                                          "placeholder": "Логин (Ваш e-mail)", "type": "email"}))
    first_name = forms.CharField(label="",
                                 widget=forms.TextInput(
                                     attrs={"class": "u-input u-input-rectangle", "id": "first_name",
                                            "placeholder": "Имя"}))

    last_name = forms.CharField(label="",
                                 widget=forms.TextInput(
                                     attrs={"class": "u-input u-input-rectangle", "id": "last_name",
                                            "placeholder": "Фамилия"}))
    city = forms.CharField(label="",
                           widget=forms.TextInput(
                               attrs={"class": "u-input u-input-rectangle", "id": "city",
                                      "placeholder": "Город"}))
    school = forms.CharField(label="",
                             widget=forms.TextInput(
                                 attrs={"class": "u-input u-input-rectangle", "id": "school",
                                        "placeholder": "Школа"}))
    s_class = forms.CharField(label="",
                              widget=forms.TextInput(
                                  attrs={"class": "u-input u-input-rectangle", "id": "s_sclass",
                                         "placeholder": "Класс"}))
    role = forms.ChoiceField(required=False, label="Роль",
                             widget=forms.Select(attrs={"class": "u-form-select-wrapper", "id": "role",
                                                        "aria-label": ""}, ),
                             choices=(("student", "Ученик"), ("teacher", "Учитель")))

    password1 = forms.CharField(label="",
                               widget=forms.PasswordInput(
                                   attrs={"type": "password", "class": "u-input u-input-rectangle", "id": "password1",
                                          "placeholder": "Введите пароль"}))
    password2 = forms.CharField(label="Повторите пароль",
                               widget=forms.PasswordInput(
                                   attrs={"type": "password", "class": "u-input u-input-rectangle", "id": "password2",
                                          "placeholder": "Повторите пароль"}))

    class Meta:
        model = CorrectUser
        fields = ('username', 'first_name', 'last_name', 's_class', 'school', 'city', 'password1', 'password2', 'role')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин", required=True,
                                 widget=forms.TextInput(
                                     attrs={"class": "u-input u-input-rectangle", "id": "username",
                                            "placeholder": "Логин", }))
    password = forms.CharField(label="Пароль", required=True,
                                 widget=forms.PasswordInput(
                                     attrs={"type": "password", "class": "u-input u-input-rectangle ", "id": "password",
                                            "placeholder": "Введите пароль", }))
