from django.shortcuts import render
from .models import ChatModel
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def index(request):
    users = User.objects.exclude(username=request.user.username)
    return render(request, 'index.html', context={'users': users})

@login_required(login_url = 'login')
def chatRoom(request, user_name):
    other_user = User.objects.get(username=user_name)
    users = User.objects.exclude(username=request.user.username)

    if request.user.id > other_user.id:
        thread_name = f'chat_{request.user.id}-{other_user.id}'
    else:
        thread_name = f'chat_{other_user.id}-{request.user.id}'
    message_objs = ChatModel.objects.filter(thread_name=thread_name)
    return render(request, 'chat_window.html', context={'user': other_user, 'users': users, 'messages': message_objs})