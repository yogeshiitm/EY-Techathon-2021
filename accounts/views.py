from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.db import models
from .forms import CustomRegisterForm
from django.urls import reverse
from django.http import HttpResponseRedirect

# User._meta.get_field('email')._blank = False
# User.add_to_class('email', models.EmailField(null=True, blank=False))
# User._meta.get_field('email')._unique = True

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('dashboard')

        else:
            messages.error(request, 'Invalid credentials!')
            return redirect('login')

    else:
        if request.user.is_authenticated:
            return redirect('/')
        else:
            return render(request, 'accounts/login.html')


def signup(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST or None)

        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')

            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = auth.authenticate(username = username,password = password)
            login(request, user)
            return redirect('dashboard')

        else:
            messages.error(request, form.errors)
            return render(request, 'accounts/signup.html' , {'form':form})

    else:
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            form = CustomRegisterForm()
            return render(request, 'accounts/signup.html' , {'form':form})


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    return render(request, 'accounts/vaccine_form.html')


@login_required(login_url='login')
def profile(request):
    user = request.user
    userdata = {
        # 'Name': user.get_full_name(),
        # 'Email': user.email,
        # 'Joined': user.date_joined, 
        # 'Last login': user.last_login,

        #test data
        'Name': 'Yogesh Agarwala',
        'Email': 'yogeshagarwala1@gmail.com',
        'Joined On': '23-01-21, 8:03 p.m.', 
        'Last login': '23-01-21, 9:14 p.m.',
    }
    return render(request, 'accounts/profile.html', {'userdata': userdata})