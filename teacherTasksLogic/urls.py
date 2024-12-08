from django.urls import path
from teacherTasksLogic.views import *
from teacherTasksLogic.views_selects import *

urls_task_logic = [
    path('create_task/', CreateTask.as_view(), name="create_task"),
    path('create_task/remove_sentence/<int:pk>/', remove_sentence, name="remove_sentence"),
    path('create_task/add_students/add/<int:id_student>/', add_student, name="add_student_to_task"),
    path('create_task/add_students/remove/<int:id_student>/', remove_student, name="remove_student_to_task"),
    path('create_task/change_date/', change_date, name="change_date_task"),
    path('create_task/change_check_phrases/', change_phrases, name="change_phrases"),
    path('create_task/срфтпу_remove_punctuation/', change_remove_punctuation, name="change_remove_punctuation"),
    path('create_task/apply/', ApplyTask.as_view(), name="apply_task"),
    path('task/<int:task_id>/', WatchTask.as_view(), name="watch_task"),
    path('task/<int:task_id>/<int:student_id>', WatchSentence.as_view(), name="watch_sentence"),
    path('task/student/<int:student_id>', WatchStudent.as_view(), name="watch_student"),
    path('task/remove/<int:task_id>', RemoveTask.as_view(), name="remove_task"),
]
