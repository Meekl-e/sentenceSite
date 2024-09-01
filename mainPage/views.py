from django.views.generic import *#TemplateView, FormView, ListView

from analysSentenceLogic.forms import NameForm
from analysSentenceLogic.models import Sentence
from utils import BaseMixin


# Create your views here.

class homePage(BaseMixin, ListView):
    template_name = 'index.html'
    model = Sentence
    context_object_name = 'sentences'
    queryset = Sentence.objects.exclude(count=1).order_by('-count')[:5]


    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        return self.get_mixin_context(context )





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




