from django import forms
from django.forms import formset_factory


class WordForm(forms.Form):
    type = forms.ChoiceField(required=True, label="", widget=forms.Select(attrs={"class": "form-select",
                                                                                  "aria-label":"", "style":"width:200px"},),
        choices=(("none","Без подчёркивания"),("line", "Подлежащее"), ("double_line", "Сказуемое"),
                 ("wavy_line", "Определение"),("dotted_circle_line", "Обстоятельство"),
                 ("dotted_line", "Дополнение"),("circle", "Союз"),))


class PartOptionChange(forms.Form):
    main_members = forms.ChoiceField(required=True, label="", widget=forms.Select(attrs={
        "class": "form-select",
        "aria-label": "",
        "style": "width:auto;display: inline-block"}, ),
                                     choices=(
                                         ("Двусоставное", "Двусоставное"),
                                         ("Односоставное определенно-личное", "Односоставное определенно-личное"),
                                         ("Односоставное неопределенно-личное", "Односоставное неопределенно-личное"),
                                         ("Односоставное обобщённо-личное", "Односоставное обобщённо-личное"),
                                         ("Односоставное безличное", "Односоставное безличное")))
    second_members = forms.ChoiceField(required=True, label="", widget=forms.Select(attrs={
        "class": "form-select",
        "aria-label": "",
        "style": "width:auto;display: inline-block"}, ),
                                       choices=(
                                           ("Распространенное", "Распространенное"),
                                           ("Нераспространенное", "Нераспространенное")))
    lost_members = forms.ChoiceField(required=True, label="", widget=forms.Select(attrs={
        "class": "form-select",
        "aria-label": "",
        "style": "width:auto;display: inline-block"}, ),
                                     choices=(
                                         ("Полное", "Полное"), ("Неполное", "Неполное")))
    difficulty_members = forms.ChoiceField(required=True, label="", widget=forms.Select(attrs={
        "class": "form-select",
        "aria-label": "",
        "style": "width:auto;display: inline-block"}, ),
                                           choices=(
                                               ("Неосложнённое", "Неосложнённое"),
                                               ("Осложнено ОЧП", "Осложнено однородными членами предложения "),
                                               ("Осложнено обособленными членами",
                                                "Осложнено компонентами, не являющихся членами предложения"),))

class RelationForm(forms.Form):
    question = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "id": "form-question",
                "class": "form-control",
                "list": "questionListOption",
                "style": "width: auto",
                "placeholder": "Введите вопрос",
                "type": "text",
            }
        )
    )
    selected = forms.CharField(max_length=1001, widget=forms.TextInput(attrs={"id":"selected_order","type":"hidden"}))

    # tokens = forms.CharField(max_length=10000, widget=forms.TextInput(attrs={"id":"tokens","type":"hidden"}))

    def __init__(self, questions=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
       # self.fields['question'].widget.attrs['questions'] = questions or []
        if questions:
            self.datalist = self.create_datalist(questions)

    def create_datalist(self, questions):
        datalist_html = '<datalist id="questionListOption">'
        for q in questions:
            datalist_html += f'<option value="{q}">'
        datalist_html += "</datalist>"
        return datalist_html


class PartForm(forms.Form):
    type = forms.ChoiceField(required=True, label="",
                             widget=forms.Select(attrs={"id": "part_type", "class": "form-select",
                                                        "aria-label": "",
                                                        }, ),
                             choices=(
                                 ("Сочинительная часть", "Сочинительная часть"),
                                 ("Подчинительная часть", "Подчинительная часть")))
    selected = forms.CharField(required=True, max_length=100,
                               widget=forms.HiddenInput(attrs={"id": "selected_order"}), )

    type_goal = forms.ChoiceField(required=False, label="",
                                  widget=forms.Select(attrs={"id": "type_goal", "class": "form-select",
                                                             "aria-label": "",
                                                             }, ),
                                  choices=(
                                      ("Повествовательное", "Повествовательное"),
                                      ("Вопросительное", "Вопросительное"),
                                      ("Побудительное", "Побудительное")))

    type_intonation = forms.ChoiceField(required=False, label="",
                                        widget=forms.Select(attrs={"id": "type_intonation", "class": "form-select",
                                                                   "aria-label": "",
                                                                   }, ),
                                        choices=(
                                            ("Невосклицательное", "Невосклицательное"),
                                            ("Восклицательное", "Восклицательное"),))

    gram_bases = forms.ChoiceField(required=False, label="",
                                   widget=forms.Select(attrs={"id": "gram_bases", "class": "form-select",
                                                              "aria-label": "",
                                                              }, ),
                                   choices=(
                                       ("Простое", "Простое"),
                                       ("Сложное", "Сложное")))

    main_members = forms.ChoiceField(required=False, label="", widget=forms.Select(attrs={
        "class": "form-select",
        "aria-label": "", }, ),
                                     choices=(
                                         ("Двусоставное", "Двусоставное"),
                                         ("Односоставное определенно-личное", "Односоставное определенно-личное"),
                                         ("Односоставное неопределенно-личное", "Односоставное неопределенно-личное"),
                                         ("Односоставное обобщённо-личное", "Односоставное обобщённо-личное"),
                                         ("Односоставное безличное", "Односоставное безличное")))
    second_members = forms.ChoiceField(required=False, label="", widget=forms.Select(attrs={
        "class": "form-select",
        "aria-label": "", }, ),
                                       choices=(
                                           ("Распространенное", "Распространенное"),
                                           ("Нераспространенное", "Нераспространенное")))
    lost_members = forms.ChoiceField(required=False, label="", widget=forms.Select(attrs={
        "class": "form-select",
        "aria-label": "",
    }, ),
                                     choices=(
                                         ("Полное", "Полное"), ("Неполное", "Неполное")))
    difficulty_members = forms.ChoiceField(required=False, label="", widget=forms.Select(attrs={
        "class": "form-select",
        "aria-label": "",
    }, ),
                                           choices=(
                                               ("Неосложнённое", "Неосложнённое"),
                                               ("Осложнено ОЧП", "Осложнено однородными членами предложения "),
                                               ("Осложнено обособленными членами",
                                                "Осложнено компонентами, не являющихся членами предложения"),))


class SchemaElem(forms.Form):
    type_line = forms.ChoiceField(required=True, label="", widget=forms.Select(attrs={"class": "form-select",
                                                                                      "aria-label": "",
                                                                                      "style": "width:auto; display:inline-block"}, ),
                                  choices=(
                                      ("none", "Без линии"), ("word", "Слово"), ("line", "Линия подлежащего"),
                                      ("double_line", "Линия сказуемого"),
                                      ("wavy_line", "Линия определения"),
                                      ("dotted_circle_line", "Линия обстоятельства"),
                                      ("dotted_line", "Линия дополнения"),))



class RemoveForm(forms.Form):
    id_remove = forms.IntegerField(required=True,  widget=forms.HiddenInput())


WordFormSet = formset_factory(WordForm, extra=0)
SchemaFormSet = formset_factory(SchemaElem, extra=0)

PartsFormSet = formset_factory(PartOptionChange, extra=0)
