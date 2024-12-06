from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView

from authLogic.forms import *
from utils import BaseMixin


class RegisterUser(CreateView):
    template_name = 'registration.html'
    form_class = RegisterFrom
    success_url = reverse_lazy('login')




    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context




class loginPage(BaseMixin, LoginView):
    authentication_form  = LoginForm
    template_name = 'enter.html'

    def form_invalid(self, form):

        error = "Неправильные имя пользователя или пароль"
        print("Eeeeee")
        data = super().get_mixin_context(super().get_context_data(auth_form=form, error=error))
        return self.render_to_response(data)
    def form_valid(self, form):
        to = self.request.GET.get("from")
        login(self.request, form.get_user())
        if to is None:
            return redirect("home")
        else:
            return HttpResponseRedirect(to)

    def get_context_data(self, **kwargs):
        data = super().get_mixin_context(super().get_context_data(auth_form=LoginForm()))
        return data



def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse(request.GET.get("from")))
