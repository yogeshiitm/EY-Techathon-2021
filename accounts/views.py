from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.db import models
from .forms import CustomRegisterForm
from django.urls import reverse
from django.http import HttpResponseRedirect
from vaccine_delivery.models import *

# User._meta.get_field('email')._blank = False
# User.add_to_class('email', models.EmailField(null=True, blank=False))
# User._meta.get_field('email')._unique = True

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)

            # if MedicalForm.objects.get(user = request.user):
            #     return redirect('vaccineform')
            # else:
            #     return redirect('dashboard')
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
            return redirect('vaccineform')

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
        'Name': user.get_full_name(),
        'Email': user.email,
        'Last login': user.last_login,

        #test data
        # 'Name': 'Yogesh Agarwala',
        # 'Email': 'yogeshagarwala1@gmail.com',
        # 'Last login': '23 Jan 2021',
    }
    return render(request, 'accounts/profile.html', {'userdata': userdata})



def vaccineform(request):

    form = MedicalForm()

    if request.method == 'POST':
        form = MedicalForm(request.POST)

        if form.is_valid():
            user = request.user
            adhaar = form.cleaned_data['adhaar']
            mobile = form.cleaned_data['mobile']
            category = form.cleaned_data['category']
            state = form.cleaned_data['state']
            district = form.cleaned_data['district']
            age = form.cleaned_data['age']
            gender = form.cleaned_data['gender']
            
            covid = form.cleaned_data['covid']
            smoker = form.cleaned_data['smoker']
            hbp_hyt = form.cleaned_data['hbp_hyt']
            respiratory = form.cleaned_data['respiratory']
            asthama = form.cleaned_data['asthma']
            chd =form.cleaned_data['chd']
            diabetes = form.cleaned_data['diabetes']
            cancer_non = form.cleaned_data['cancer']
            hmt = form.cleaned_data['hmt']
            reduced_kidney = form.cleaned_data['reduced_kidney']
            kidney_dialysis = form.cleaned_data['kidney_dialysis']
            liver_disease =form.cleaned_data['liver_disease']
            other_neuro = form.cleaned_data['other_neuro']
            organ_transplant =form.cleaned_data['organ_transplant']

            detail = MedicalFormModel(user,adhaar,mobile,category,state,district,age,gender,covid,smoker,hbp_hyt,respiratory,asthama,chd,diabetes,cancer_non,hmt,reduced_kidney,kidney_dialysis,liver_disease,other_neuro,organ_transplant)
            detail.save()

            return redirect('dashboard')

    states = StateModel.objects.all().order_by('state')
    return render(request, 'accounts/vaccine_form.html',{'form':form,'states':states})
