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
from django.contrib.auth import login as auth_login # https://stackoverflow.com/a/39316967/13962648


# User._meta.get_field('email')._blank = False
# User.add_to_class('email', models.EmailField(null=True, blank=False))
# User._meta.get_field('email')._unique = True

def login(request):
    if request.method == 'POST':
        states = request.POST.get('search')
        if states is not None:
            try:
                state = StateModel.objects.get(state = states)
                print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = states)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('signup')

        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)

            # if MedicalForm.objects.get(user = request.user):
            #     return redirect('vaccineform')
            # else:
            #     return redirect('dashboard')
            return redirect('vaccineform')

        else:
            messages.error(request, 'Invalid credentials!')
            return redirect('login')

    else:
        if request.user.is_authenticated:
            return redirect('vaccineform')
        else:
            return render(request, 'accounts/login.html')


def signup(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST or None)

        states = request.POST.get('search')
        if states is not None:
            try:
                state = StateModel.objects.get(state = states)
                print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = states)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('signup')

        if form.is_valid():
            user = form.save()
            form.save()
            #messages.success(request, 'Account created successfully!')

            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            #inactive_user = send_verification_email(request, form)
            user = auth.authenticate(email=email, password = password)
    

            # https://stackoverflow.com/a/39316967/13962648
            # login(request, user)
            auth_login(request, user)
            return redirect('vaccineform')

        else:
            messages.error(request, form.errors)
            return render(request, 'accounts/signup.html' , {'form':form})

    else:
        if request.user.is_authenticated:
            return redirect('vaccineform')
        else:
            form = CustomRegisterForm()
            return render(request, 'accounts/signup.html' , {'form':form})


def logout_user(request):
    if request.method == 'POST':
        states = request.POST.get('search')
        if states is not None:
            try:
                state = StateModel.objects.get(state = states)
                print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = states)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('signup')
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    if request.method == 'POST':
        states = request.POST.get('search')
        try:
            state = StateModel.objects.get(state = states)
            print(state)
            return redirect(f'/district_level/{state.state}')
            
        except StateModel.DoesNotExist:
            try :
                district = DistrictModel.objects.get(district = states)
                return redirect(f'/district_level/{district.state}')
            except DistrictModel.DoesNotExist:
                return redirect('dashboard')

    email = request.user.email
    name = request.user.first_name

    try:
        user = MedicalModel.objects.get(user=request.user)  
        context={
            'email':email,
            'name':name,
            'user':user,
        }
        return render(request, 'accounts/dashboard.html',context)

    except MedicalModel.DoesNotExist:
        return redirect('vaccineform')


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

#####################################################################


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
    if request.method == 'GET':
        try:
            med = MedicalModel.objects.get(user=request.user)
            return redirect('dashboard')

        except MedicalModel.DoesNotExist:   
            form = MedicalForm()

            states = StateModel.objects.all().order_by('state')
            return render(request, 'accounts/vaccine_form.html',{'form':form,'states':states})
        # if MedicalModel.objects.get(user=request.user):
        #     form = MedicalModel.objects.get(user=request.user)
        #     return render(request,'accounts/vaccine_form.html',{'form':form,'states':states})


    if request.method == 'POST':
        states = request.POST.get('search')
        if states is not None:
            try:
                state = StateModel.objects.get(state = states)
                print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = states)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('signup')

        form = MedicalForm(request.POST)

        user = request.user
        adhaar = request.POST.get('adhaar')
        mobile = request.POST.get('mobile')
        pincode = request.POST.get('pincode')
        occupation = request.POST.get('occupation')
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

        detail = MedicalModel(user = user,adhaar = adhaar,mobile = mobile,pincode=pincode,occupation=occupation,state=state,district=district,age=age,gender=gender,covid=covid,smoker=smoker,hbp_hyt=hbp_hyt,respiratory=respiratory,chd=chd,diabetes=diabetes,cancer_non=cancer_non,hmt=hmt,reduced_kidney=reduced_kidney,kidney_dialysis=kidney_dialysis,liver_disease=liver_disease,strk_dmtia=strk_dmtia,other_neuro=other_neuro,organ_transplant=organ_transplant)
        detail.save()
        detail.get_category()
        detail.set_eligibility()
        return redirect('dashboard')

    






