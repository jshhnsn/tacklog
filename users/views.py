from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse


# Create your views here.
def register(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f'Account successfully created for {user}. Please login to continue.')
            return redirect(reverse('login'))
    
    print(form.errors.as_json())
    return render(request, 'users/register.html', {
        'form' : form
    })

def login(request):
    form = AuthenticationForm()
    return render(request, 'users/login.html', {
        'form' : form
    })