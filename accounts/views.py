from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.db import models
from .forms import *
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import *
from vaccine_delivery.models import *

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
            return redirect('vaccineform')

        else:
            messages.error(request, form.errors)
            return render(request, 'accounts/signup.html' , {'form':form})

    else:
        if request.user.is_authenticated:
            if MedicalModel.objects.get(user=request.user):
                return redirect('dashboard')
            return redirect('vaccineform')
        else:
            form = CustomRegisterForm()
            return render(request, 'accounts/signup.html' , {'form':form})


def logout_user(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
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
    return render(request, 'accounts/dashboard.html', {'userdata': userdata})



def get_binary(request,_data):
    data = request.POST.get(f'{_data}')
    if _data == 'covid':
        data = request.POST.get(f'{_data}')
        if data is None:
            return 1
        else:
            return 0
    if data is not None:
        return int(data)
    else:
        return 0
    

@login_required(login_url='login')
def vaccineform(request):
    try:
        med = MedicalModel.objects.get(user=request.user)
        return redirect('dashboard')

    except MedicalModel.DoesNotExist:   
        form = MedicalForm()

        states = StateModel.objects.all().order_by('state')
        # if MedicalModel.objects.get(user=request.user):
        #     form = MedicalModel.objects.get(user=request.user)
        #     return render(request,'accounts/vaccine_form.html',{'form':form,'states':states})


        if request.method == 'POST':
            form = MedicalForm(request.POST)

            user = request.user
            adhaar = request.POST.get('adhaar')
            mobile = request.POST.get('mobile')
            pincode = request.POST.get('pincode')
            category = request.POST.get('category')
            state = request.POST.get('state')
            district = request.POST.get('district')
            age = request.POST.get('dob')
            gender = request.POST.get('gender') 
            
            # if gender or state or adhaar or district or mobile or category is None:
            #     states = StateModel.objects.all().order_by('state')
            #     return render(request,'accounts/vaccine_form.html',{'form':MedicalForm(request.POST),'states':states})
            
            covid = get_binary(request,'covid')
            smoker = get_binary(request,'smoker')
            hbp_hyt = get_binary(request,'hbp_hyt')
            respiratory = get_binary(request,'respiratory')
            chd =get_binary(request,'chd')
            diabetes = get_binary(request,'diabetes') 
            cancer_non = get_binary(request,'cancer_non')
            hmt = get_binary(request,'hmt')
            reduced_kidney = get_binary(request,'reduced_kidney')
            kidney_dialysis = get_binary(request,'kidney_dialysis')
            liver_disease =get_binary(request,'liver_disease')
            strk_dmtia = get_binary(request,'strk_dmtia')
            other_neuro = get_binary(request,'other_neuro')
            organ_transplant =get_binary(request,'organ_transplant')

            detail = MedicalModel(user = user,adhaar = adhaar,mobile = mobile,pincode=pincode,category=category,state=state,district=district,age=age,gender=gender,covid=covid,smoker=smoker,hbp_hyt=hbp_hyt,respiratory=respiratory,chd=chd,diabetes=diabetes,cancer_non=cancer_non,hmt=hmt,reduced_kidney=reduced_kidney,kidney_dialysis=kidney_dialysis,liver_disease=liver_disease,strk_dmtia=strk_dmtia,other_neuro=other_neuro,organ_transplant=organ_transplant)
            detail.save()

            return redirect('dashboard')

        return render(request, 'accounts/vaccine_form.html',{'form':form,'states':states})



