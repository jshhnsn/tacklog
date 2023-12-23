from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse



def register_page(request):
    # Generate account creation form.
    form = UserCreationForm()

    # Check if the user is submitting the form.
    if request.method == 'POST':
        # Create the form from the request.
        form = UserCreationForm(request.POST)

        # Check if the form is valid.
        if form.is_valid():
            # Save user to database.
            form.save()
            # Redirect to the login page with a message confirming the account 
            # has been created.
            user = form.cleaned_data.get('username')
            messages.success(request, f'''Account successfully created for 
                             <strong>{user}</strong>. Please log in to 
                             continue.''')
            return redirect('login')
    
    # If user is logged in, send them to the search page.
    if request.user.is_authenticated:
        return redirect('search')

    # If not submitting a form, render registration form.
    return render(request, 'users/register.html', {
        'form' : form
    })


def login_page(request):

    # Check if user if submitting the form.
    if request.method == 'POST':

        # Get user name and password from the request
        username = request.POST['username']
        password = request.POST['password']
        # Attempt to get the user from the database.
        user = authenticate(request, username=username, password=password)
        # Get the next page value if exists.
        next = request.POST.get('next')

        # If user exists.
        if user is not None:
            # Log user in.
            login(request, user)
            # Redirect to the next value or search page if none.
            if next is not None:
                return redirect(next)
            return redirect('search')
        
        # If user doesn't exist.
        else:
            # Generate error message.
            messages.info(request, 'Username or password is incorrect', 
                          extra_tags='fail')

    # If user is logged in, send them to the search page.
    if request.user.is_authenticated:
        return redirect('search')
    
    # Create login form and render the login page.
    form = AuthenticationForm()
    return render(request, 'users/login.html', {
        'form' : form
    })


def logout_user(request):
    # Log user out.
    logout(request)
    # Redirect to the login page.
    return redirect('login')