from django.urls import path

from . import views

urlpatterns = [
    path('<str:user_name>/', views.chatRoom, name='chat'),
]