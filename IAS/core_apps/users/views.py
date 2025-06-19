from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.urls import reverse

from IAS.core_apps.users.forms import LoginForm, RegistrationForm

# Create your views here.


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Handle form data here
            status, _message = form.save()
            if status:
                messages.success(request, _message)
                return redirect(reverse('Login'))
            messages.warning(request, f'{_message}')
            return redirect(reverse('Register'))
        else:
            messages.warning(request, f'{form.errors}')
            return redirect(reverse('Register'))
    else:
        form = RegistrationForm()
    context = {'form': form}
    return render(request, "users/register.html", context)


def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Handle form data here
            _, url_name, _message = form.make_user_session(request)
            messages.success(request, _message)
            return redirect(reverse(f'{url_name}'))
    else:
        form = LoginForm()

    context = {'form': form}
    return render(request, "users/login.html", context)


def user_logout(request):
    logout(request)
    messages.info(request, "Logged Out Successfully!")
    return redirect("Login")
