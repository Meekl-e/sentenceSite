from django.urls import path

from changeSentenceLogic.views_first_stage import *
from changeSentenceLogic.views_second_stage import *
from changeSentenceLogic.views_save import *

urls_change = [
    path('sentence/<int:pk>/change/', ChangeSentence.as_view(), name='change_sentence'),
    path('sentence/<int:pk>/change/remove/', remove_sentence, name='remove_relation'),
    path('sentence/<int:pk>/change/edit_token/<int:token_id_0>/', edit_token_text, name='edit_token'),
    path('sentence/<int:pk>/change/edit_pos/<int:token_id_0>/', edit_pos_text, name='edit_pos'),
    path('sentence/<int:pk>/change/edit_type/<int:token_id_0>/', edit_type_text, name='edit_type'),
    path('sentence/<int:pk>/change/remove_token/<int:token_id_0>/', remove_token, name='remove_token'),
    path('sentence/<int:pk>/change/add_token/<int:token_id>/', add_token, name='add_token'),
    path('sentence/<int:pk>/change/edit_line/<int:token_id_0>/', edit_line, name='edit_line'),
    path('sentence/<int:pk>/change_part/', ChangeParts.as_view(), name='change_parts'),
    path('sentence/<int:pk>/change_part/add_part', add_part, name='add_part'),
    path('sentence/<int:pk>/change_part/remove_part/<int:id>', remove_part, name='remove_part'),
    path('sentence/<int:pk>/change_part/<int:id_part>/change_elem/<str:type>', change_elem, name='change_elem'),
    path('sentence/<int:pk>/change_part/save/', save_sentence, name='save_sentence'),
]
