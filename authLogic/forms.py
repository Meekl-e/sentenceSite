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
    second_last_name = forms.CharField(required=False, label="",
                                       widget=forms.TextInput(
                                           attrs={"class": "u-input u-input-rectangle", "id": "second_last_name",
                                                  "placeholder": "Ваше отчество (при наличии)"}))

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
    s_class = forms.ChoiceField(required=False, label="Класс",
                                widget=forms.Select(attrs={"class": "u-input u-input-rectangle", "id": "s_class",
                                                           "aria-label": ""}, ),
                                choices=(
                                ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"),
                                ("8", "8"), ("9", "9"), ("10", "10"), ("11", "11"), ("Не в школе", "Не в школе")))

    role = forms.ChoiceField(required=False, label="Роль",
                             widget=forms.Select(attrs={"class": "u-input u-input-rectangle", "id": "role",
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
        fields = ('username', 'first_name', 'last_name', 's_class', 'school', 'city', 'password1', 'password2', 'role',
                  'second_last_name')

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин", required=True,
                                 widget=forms.TextInput(
                                     attrs={"class": "u-input u-input-rectangle", "id": "username",
                                            "placeholder": "Логин", }))
    password = forms.CharField(label="Пароль", required=True,
                                 widget=forms.PasswordInput(
                                     attrs={"type": "password", "class": "u-input u-input-rectangle ", "id": "password",
                                            "placeholder": "Введите пароль", }))
