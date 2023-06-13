from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            new_user = form.save()
            
            login(request, new_user)

            return redirect('home')

    else:
        form = CustomUserCreationForm()

    return render(request, 'account/register.html', {'form': form})


def loginView(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            if user.is_active:
        
                login(request, user)
                return redirect('home')
            else:
                return HttpResponse("Account Not Active")
        else:
            context = {'notfound': True}
            
            return render(request, 'account/login.html', context)

    else:
        return render(request, 'account/login.html')