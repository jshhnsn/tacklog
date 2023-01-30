from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse


# Create your views here.
def register_page(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Account successfully created for <strong>{user}</strong>. Please log in to continue.')
            return redirect('login')
    
    return render(request, 'users/register.html', {
        'form' : form
    })

def login_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('search')
        else:
            messages.info(request, 'Username or password is incorrect', extra_tags='fail')

    form = AuthenticationForm()
    return render(request, 'users/login.html', {
        'form' : form
    })

def logout_user(request):
    logout(request)
    return redirect('login')