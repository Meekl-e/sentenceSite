from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView, ListView
from mainPage.sentParsing.parser import parsing

from .forms import NameForm
from .models import Sentence
from utils import BaseMixin
from .model_changer import create_sentence
# Create your views here.

class homePage(BaseMixin, ListView):
    template_name = 'index.html'
    model = Sentence
    context_object_name = 'sentences'
    queryset = Sentence.objects.exclude(count=1).order_by('-count')[:5]


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return self.get_mixin_context(context,sentence_form=NameForm )





class aboutPage(BaseMixin, TemplateView):
    template_name = 'about.html'



    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return self.get_mixin_context(context)



class studentPage(BaseMixin, TemplateView):
    template_name = 'student.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return self.get_mixin_context(context)


class teacherPage(BaseMixin, TemplateView):
    template_name = 'teacher.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return self.get_mixin_context(context)


class checkSentencePage(BaseMixin, FormView):
    template_name = "sentence_result.html"
    form_class = NameForm

    def form_valid(self, form):
        data = super().get_mixin_context(super().get_context_data(sentence_form=NameForm))
        data["pars_result"], pars = parsing(form.cleaned_data["text"])
        create_sentence(pars)
        return self.render_to_response(context=data)

    def get_context_data(self, **kwargs):

        return reverse_lazy("home")





