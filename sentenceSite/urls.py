"""
URL configuration for sentenceSite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from analysSentenceLogic.views import *
from authLogic.views import *
from changeSentenceLogic.views_first_stage import *
from changeSentenceLogic.views_second_stage import *
from mainPage.views import *
from userLogic.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homePage.as_view(), name='home'),
    path('about/', aboutPage.as_view()),
    path('student/', studentPage.as_view()),
    path('teacher/', teacherPage.as_view()),
    path('registration/', RegisterUser.as_view(), name='registration'),
    path('login/', loginPage.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('check_sentence/', checkSentencePage.as_view(), name='check_sentence'),
    path('sentence/<int:pk>/', SentencePage.as_view(), name='sentence'),
    path('sentence/', ViewRequest.as_view(), name='view_request'),
    path('like/<int:pk>/', addLike, name='like'),
    path('dislike/<int:pk>/', addDisLike, name='dislike'),
    path('favourite/<int:pk>/', addFavourite, name='favourite'),
    path('sentence/<int:pk>/change/', ChangeSentence.as_view(), name='change_sentence'),
    path('sentence/<int:pk>/change/remove/', remove_sentence, name='remove_relation'),
    path('sentence/<int:pk>/change/edit_token/<int:token_id_0>/', edit_token_text, name='edit_token'),
    path('sentence/<int:pk>/change/edit_pos/<int:token_id_0>/', edit_pos_text, name='edit_pos'),
    path('sentence/<int:pk>/change/remove_token/<int:token_id_0>/', remove_token, name='remove_token'),
    path('sentence/<int:pk>/change/add_token/<int:token_id>/', add_token, name='add_token'),
    path('sentence/<int:pk>/change/edit_line/<int:token_id_0>/', edit_line, name='edit_line'),
    path('sentence/<int:pk>/change_part/', ChangeParts.as_view(), name='change_parts'),
    path('sentence/<int:pk>/change_part/add_part', add_part, name='add_part'),
    path('sentence/<int:pk>/change_part/save/', SaveSentence.as_view(), name='save_parts'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


