from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from utils import BaseMixin
from authLogic.forms import *
from mainPage.forms import NameForm

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
        form.errors["__all__"] = "Неправильные имя пользователя или пароль"
        data = super().get_mixin_context(super().get_context_data(auth_form=form, sentence_form=NameForm))
        return self.render_to_response(data)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['auth_form'] = self.get_form()
        return context



def logout_user(request):
    logout(request)
    return redirect('home')

