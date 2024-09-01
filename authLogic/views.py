from django.contrib.auth import logout, login, authenticate

from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from analysSentenceLogic.models import Sentence
from utils import BaseMixin
from authLogic.forms import *
from analysSentenceLogic.forms import NameForm

class RegisterUser(CreateView):
    template_name = 'registration.html'
    form_class = RegisterFrom
    success_url = reverse_lazy('home')



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["entrance"] = True
        return context




class loginPage(BaseMixin, LoginView):
    authentication_form  = LoginForm
    template_name = 'index.html'

    def form_invalid(self, form):
        to = self.request.GET.get("from")
        form.errors["__all__"] = "Неправильные имя пользователя или пароль"

        data = super().get_mixin_context(super().get_context_data(auth_form=form))
        data["sentences"] = Sentence.objects.exclude(count=1).order_by("-count")[:5]
        return self.render_to_response(data)
    def form_valid(self, form):
        to = self.request.GET.get("from")
        login(self.request, form.get_user())
        print(self.request.path)
        if to is None:
            return redirect("home")
        else:
            return HttpResponseRedirect(to)


    def get(self,request,*args, **kwargs):
        return redirect('home')



def logout_user(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get("from"))

