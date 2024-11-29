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
from changeSentenceLogic.urls import urls_change
from changeSentenceLogic.views_first_stage import *
from changeSentenceLogic.views_second_stage import *
from mainPage.views import *
from studentTasksLogic.views import *
from teacherTasksLogic.urls import urls_task_logic
from teacherTasksLogic.views import *
from teacherTasksLogic.views_selects import *
from userLogic.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homePage.as_view(), name='home'),
    path('accounts/login/', homePage.as_view()),
    path('about/', aboutPage.as_view()),
    path('student/', studentPage.as_view(), name="student_page"),
    path('teacher/', teacherPage.as_view(), name="teacher_page"),
    path('registration/', RegisterUser.as_view(), name='registration'),
    path('login/', loginPage.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('check_sentence/', checkSentencePage.as_view(), name='check_sentence'),
    path('sentence/<int:pk>/', SentencePage.as_view(), name='sentence'),
    path('sentence/', ViewRequest.as_view(), name='view_request'),
    path('like/<int:pk>/', addLike, name='like'),
    path('dislike/<int:pk>/', addDisLike, name='dislike'),
    path('favourite/<int:pk>/', addFavourite, name='favourite'),
    path('get_invite_link/', get_invite_link, name='get_invite_link'),
    path('add_student/<str:code>', AddStudent2Teacher.as_view(), name='add_student_link'),
    path('remove_student/<int:id_student>', RemoveStudentFromTeacher.as_view(), name='remove_student'),
    path('task/<int:id_task>', TaskView.as_view(), name='task'),
    path('task/edit/<int:sent_id>/<int:id_task>/', sent_task, name='sent_task'),

    *urls_change,
    *urls_task_logic



]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


