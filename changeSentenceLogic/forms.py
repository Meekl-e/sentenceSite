from django import forms
from django.forms import formset_factory


class WordForm(forms.Form):
    type = forms.ChoiceField(required=True, label="", widget=forms.Select(attrs={"class": "form-select",
                                                                                  "aria-label":"", "style":"width:200px"},),
        choices=(("none","Без подчёркивания"),("line", "Подлежащее"), ("double_line", "Сказуемое"),
                 ("wavy_line", "Определение"),("dotted_circle_line", "Обстоятельство"),
                 ("dotted_line", "Дополнение"),("circle", "Союз"),))


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
                             widget=forms.Select(attrs={"id": "part-type", "class": "form-select",
                                                        "aria-label": "",
                                                        }, ),
                             choices=(
                                 ("composition", "Сочинительная часть"), ("subordination", "Подчинительная часть")))
    selected = forms.CharField(required=True, max_length=100,
                               widget=forms.HiddenInput(attrs={"id": "selected_order"}), )





class RemoveForm(forms.Form):
    id_remove = forms.IntegerField(required=True,  widget=forms.HiddenInput())

WordFormSet = formset_factory(WordForm, extra=0)


class SendForm(forms.Form):
    pass
