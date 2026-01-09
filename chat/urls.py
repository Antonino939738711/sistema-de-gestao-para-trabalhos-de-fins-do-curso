from django.urls import path
from . import views

urlpatterns = [
    path('<int:user_id>/', views.chat_view, name='chat'),
    path('<int:user_id>/enviar/', views.enviar_mensagem, name='enviar_mensagem'),
    path('tutor/estudantes/', views.tutor_chat_estudantes, name='tutor_chat_estudantes'),
    path('tutor/<int:estudante_id>/', views.chat_tutor, name='chat_tutor'),
    path('tutor/<int:estudante_id>/enviar/', views.chat_tutor_enviar, name='chat_tutor_enviar'),
]
