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
from django.contrib.auth import login as auth_login # https://stackoverflow.com/a/39316967/13962648
from django_email_verification import send_email
from django.contrib.auth import get_user_model
import datetime
from django.db.models import Q #https://stackoverflow.com/a/45988838/13962648


# User._meta.get_field('email')._blank = False
# User.add_to_class('email', models.EmailField(null=True, blank=False))
# User._meta.get_field('email')._unique = True

def login(request):
    if request.method == 'POST':
        search = request.POST.get('search')
        if search is not None:

            arr1=search.split()
            arr2=[]
            for str in arr1:
                if str.lower() !='and':
                    arr2.append(str.capitalize())
                else:
                    arr2.append(str.lower())
            formattedSearch = ' '.join(arr2)

            try:
                state = StateModel.objects.get(state = formattedSearch)
                print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = formattedSearch)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('signup')

        email = request.POST['email']
        password = request.POST['password']
        # user = auth.authenticate(email=email, password=password)
        user = get_user_model().objects.filter(email=email).first()
        #print(user,'\n')

        if user is None:
            # user did not exists
            messages.error(request, 'Email is not registered, please signup first!')
            return redirect('login')

        elif not user.is_active:
            # user is not active
            messages.error(request, 'Email is not verified yet!')
            return redirect('login')

        else:
            # password was incorrect
            user = auth.authenticate(email=email, password=password)

            #checking which login button was pressed
            if request.POST.get('UserLogin')== 'True':
                if user is not None:
                    # If the account is valid and active, we can log the user in.
                    # We'll send the user back to the homepage.
                    auth.login(request, user)
                    # if MedicalForm.objects.get(user = request.user):
                    #     return redirect('vaccineform')
                    # else:
                    #     return redirect('dashboard')
                    return redirect('vaccineform')

                else:
                    messages.error(request, 'Invalid credentials!')
                    return redirect('login')

            if request.POST.get('HealthAdminLogin')== 'True':
                if user is not None and user.is_staff:
                    auth.login(request, user)

                    # if MedicalForm.objects.get(user = request.user):
                    #     return redirect('vaccineform')
                    # else:
                    #     return redirect('dashboard')
                    return redirect('healthadmin')

                else:
                    messages.error(request, 'The email address provided is not registered as a Health administrator please contact the site admin!')
                    return redirect('login')

            if request.POST.get('VaccinationInchargeLogin')== 'True':
                if user is not None and user.is_staff:
                    auth.login(request, user)

                    return redirect('vaccination_incharge')

                else:
                    messages.error(request, 'The email address provided is not registered as a Vaccination Incharge please contact the site admin!')
                    return redirect('login')

    else:
        if request.user.is_authenticated and request.user.is_superuser:
            return redirect('vaccineform')
        elif request.user.is_authenticated and request.user.is_staff:
            # return redirect('vaccineform')
            return redirect('index')
        elif request.user.is_authenticated:
            return redirect('vaccineform')
        else:
            return render(request, 'accounts/login.html')


def signup(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST or None)

        if request.POST.get('admin')== 'True':
            if form.is_valid():
                form.save()

                #https://stackoverflow.com/a/46284838/13962648
                email = form.cleaned_data['email']
                password = form.cleaned_data['password1']
                user = auth.authenticate(email=email, password = password)

                #user set to inactive so that we can see and make the verify if the user is staff -- in future we can create a separate category/group for this users so that
                user.is_active = False
                print(user.is_active,'\n')

                messages.info(request, "Your details have been submitted, please wait till you are approved!")
                return render(request, 'accounts/signup.html' , {'form':form})
            else:
                messages.error(request, form.errors)
                return render(request, 'accounts/signup.html' , {'form':form})


        search = request.POST.get('search')
        if search is not None:

            arr1=search.split()
            arr2=[]
            for str in arr1:
                if str.lower() !='and':
                    arr2.append(str.capitalize())
                else:
                    arr2.append(str.lower())
            formattedSearch = ' '.join(arr2)

            try:
                state = StateModel.objects.get(state = formattedSearch)
                print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = formattedSearch)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('signup')

        if form.is_valid():

            form.save()
            # messages.success(request, 'Please confirm your email!')

            #https://stackoverflow.com/a/46284838/13962648
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = auth.authenticate(email=email, password = password)

            #email verification
            user.is_active = False
            send_email(user)
    
            messages.info(request, "We have sent a confirmation email to your email address. In case you do not find it, please check your spam folder!")
            return render(request, 'accounts/signup.html' , {'form':form})

            # auto login after signup
            # https://stackoverflow.com/a/39316967/13962648
            # auth_login(request, user)
            # return redirect('vaccineform')

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
    if request.method == 'POST':
        search = request.POST.get('search')
        if search is not None:

            arr1=search.split()
            arr2=[]
            for str in arr1:
                if str.lower() !='and':
                    arr2.append(str.capitalize())
                else:
                    arr2.append(str.lower())
            formattedSearch = ' '.join(arr2)

            try:
                state = StateModel.objects.get(state = formattedSearch)
                print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = formattedSearch)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('signup')
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    if request.method == 'POST':
        search = request.POST.get('search')
        if search is not None:

            arr1=search.split()
            arr2=[]
            for str in arr1:
                if str.lower() !='and':
                    arr2.append(str.capitalize())
                else:
                    arr2.append(str.lower())
            formattedSearch = ' '.join(arr2)

            try:
                state = StateModel.objects.get(state = formattedSearch)
                print(state)
                return redirect(f'/district_level/{state.state}')
                
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = formattedSearch)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('dashboard')

    email = request.user.email
    name = request.user.first_name + ' ' + request.user.last_name

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
            print(states,'\n')
            return render(request, 'accounts/vaccine_form.html',{'form':form,'states':states})
        # if MedicalModel.objects.get(user=request.user):
        #     form = MedicalModel.objects.get(user=request.user)
        #     return render(request,'accounts/vaccine_form.html',{'form':form,'states':states})


    if request.method == 'POST':
        search = request.POST.get('search')
        if search is not None:

            arr1=search.split()
            arr2=[]
            for str in arr1:
                if str.lower() !='and':
                    arr2.append(str.capitalize())
                else:
                    arr2.append(str.lower())
            formattedSearch = ' '.join(arr2)

            try:
                state = StateModel.objects.get(state = formattedSearch)
                print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = formattedSearch)
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


# @login_required(login_url='login')
# def healthadmin(request):
#     if request.method == 'POST':
#         search = request.POST.get('search')
#         if search is not None:

#             arr1=search.split()
#             arr2=[]
#             for str in arr1:
#                 if str.lower() !='and':
#                     arr2.append(str.capitalize())
#                 else:
#                     arr2.append(str.lower())
#             formattedSearch = ' '.join(arr2)

#             try:
#                 state = StateModel.objects.get(state = formattedSearch)
#                 print(state)
#                 return redirect(f'/district_level/{state.state}')
            
#             except StateModel.DoesNotExist:
#                 try :
#                     district = DistrictModel.objects.get(district = formattedSearch)
#                     return redirect(f'/district_level/{district.state}')
#                 except DistrictModel.DoesNotExist:
#                     return redirect('healthadmin')

#         category = int(request.POST.get('category'))
#         age = request.POST.get('age')
#         state = request.POST.get('state')
#         district = request.POST.get('district')
#         no_vaccines = int(request.POST.get('vaccine'))
#         email = request.user.email
#         name = request.user.first_name + ' ' + request.user.last_name

#         if age == '1':
#             users = MedicalModel.objects.filter(category= category, state=state, district=district).order_by('-illness_score')[:no_vaccines]
#             return render(request, 'accounts/health_admin.html',{'name':name,'email':email, 'users':users})
#             #all
        
#         if age == '2':
#             if category == 4:
#                 users = MedicalModel.objects.filter(age__gte = str(60), state=state,district=district).order_by('-illness_score')[:no_vaccines]
#                 return render(request, 'accounts/health_admin.html',{'name':name,'email':email,'users':users})
#             else:
#                 users = MedicalModel.objects.filter(category= category, age__gte = str(60), state=state,district=district).order_by('-illness_score')[:no_vaccines]
#                 return render(request, 'accounts/health_admin.html',{'name':name,'email':email,'users':users})
#                 #60+
        
#         if age == '3':
#             users = MedicalModel.objects.filter(category= category, age__lte = str(59), state=state,district=district).order_by('-illness_score')[:no_vaccines]
#             return render(request, 'accounts/health_admin.html',{'name':name,'email':email,'users':users})
#             #60-

#     if request.method == 'GET':

#         states = StateModel.objects.all().order_by('state')

#         email = request.user.email
#         name = request.user.first_name + ' ' + request.user.last_name

#         return render(request, 'accounts/health_admin.html',{'name':name,'email':email, 'states':states})


@login_required(login_url='login')
def healthadmin(request):
    if request.method == 'POST':
        search = request.POST.get('search')
        if search is not None:

            arr1=search.split()
            arr2=[]
            for str in arr1:
                if str.lower() !='and':
                    arr2.append(str.capitalize())
                else:
                    arr2.append(str.lower())
            formattedSearch = ' '.join(arr2)

            try:
                state = StateModel.objects.get(state = formattedSearch)
                print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = formattedSearch)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('healthadmin')

        #category = int(request.POST.get('category'))
        #age = request.POST.get('age')
        state = request.POST.get('state')
        district = request.POST.get('district')
        no_vaccines = int(request.POST.get('vaccine'))
        email = request.user.email
        name = request.user.first_name + ' ' + request.user.last_name

        states = StateModel.objects.all().order_by('state')

        age='1'
        category=5


        if age == '1':
            print('1\n')
            if category == 5:
                users = MedicalModel.objects.filter(state=state, district=district).order_by('-illness_score')
            elif category == 3:
                users = MedicalModel.objects.filter(Q(category=3) | Q(category=2), no_illness__gte = 1, state=state, district=district).order_by('-illness_score')
            elif category == 4:
                # method 1 - not working
                # users = MedicalModel.objects.filter(category= 2 or 4 ,  no_illness= 0, state=state, district=district).order_by('-illness_score')

                # method 2 - working
                # users1 = MedicalModel.objects.filter(category= 2,  no_illness= 0, state=state, district=district).order_by('-illness_score')
                # users2 = MedicalModel.objects.filter(category= 4,  no_illness= 0, state=state, district=district).order_by('-illness_score')
                # users=users1 | users2
                # users=users1 or users2 ----not working

                # method 3 -working 
                #https://stackoverflow.com/a/45988838/13962648
                users = MedicalModel.objects.filter(Q(category=2) | Q(category=4),  no_illness= 0, state=state, district=district).order_by('-illness_score')
            else:
                users = MedicalModel.objects.filter(category= category, state=state, district=district).order_by('-illness_score')
                #all

        if age == '2':
            print('2\n')
            if category == 5:
                users = MedicalModel.objects.filter( age__gte = 60, state=state, district=district).order_by('-illness_score')
            elif category == 4:
                users = MedicalModel.objects.filter(category= 2, no_illness = 0, state=state,district=district).order_by('-illness_score')[:no_vaccines]

            elif category == 3:
                users = MedicalModel.objects.filter(category= 2, no_illness__gte = 1, state=state,district=district).order_by('-illness_score')[:no_vaccines]

            else:
                users = MedicalModel.objects.filter(category= category, age__gte = 60, state=state,district=district).order_by('-illness_score')[:no_vaccines]
                #60+

        if age == '3':
            print('3\n')
            if category == 5:
                users = MedicalModel.objects.filter( age__lte = 60, state=state, district=district).order_by('-illness_score')
            else:
                users = MedicalModel.objects.filter(category= category, age__lte = 59, state=state,district=district).order_by('-illness_score')[:no_vaccines]
            #60-
        
        try:
            user = MedicalModel.objects.get(user=request.user)  
            context={
                'email':email,
                'name':name,
                'user':user,
                'users':users,
                'states':states
            }

        except MedicalModel.DoesNotExist:
            #user = MedicalModel.objects.get(user=request.user)  
            context={
                'email':email,
                'name':name,
                #'user':user,
                'users':users,
                'states':states
            }
        return render(request, 'accounts/health_admin.html',context)

    if request.method == 'GET':
        if request.user.is_staff:

            # states = StateModel.objects.all().order_by('state')
            # email = request.user.email
            # name = request.user.first_name + ' ' + request.user.last_name
            # return render(request, 'accounts/health_admin.html',{'name':name,'email':email, 'states':states})

            try:
                states = StateModel.objects.all().order_by('state')
                email = request.user.email
                name = request.user.first_name + ' ' + request.user.last_name
                user = MedicalModel.objects.get(user=request.user)  
                context={
                    'email':email,
                    'name':name,
                    'user':user,
                    'states':states
                }
                return render(request, 'accounts/health_admin.html',context)

            except MedicalModel.DoesNotExist:
                states = StateModel.objects.all().order_by('state')
                email = request.user.email
                name = request.user.first_name + ' ' + request.user.last_name
                #user = MedicalModel.objects.get(user=request.user)  
                context={
                    'email':email,
                    'name':name,
                    #'user':user,
                    'states':states
                }
                return render(request, 'accounts/health_admin.html',context)

        else:
            #return redirect('dashboard')
            messages.error(request, 'The email address provided is not registered as Health administrator please contact the site admin!')
            return render(request, 'accounts/login.html')



# def vaccination_incharge(request):
#     if request.method == 'POST':
#         search = request.POST.get('search')
#         if search is not None:

#             arr1=search.split()
#             arr2=[]
#             for str in arr1:
#                 if str.lower() !='and':
#                     arr2.append(str.capitalize())
#                 else:
#                     arr2.append(str.lower())
#             formattedSearch = ' '.join(arr2)

#             try:
#                 state = StateModel.objects.get(state = formattedSearch)
#                 print(state)
#                 return redirect(f'/district_level/{state.state}')
            
#             except StateModel.DoesNotExist:
#                 try :
#                     district = DistrictModel.objects.get(district = formattedSearch)
#                     return redirect(f'/district_level/{district.state}')
#                 except DistrictModel.DoesNotExist:
#                     return redirect('signup')

#         email = request.POST['email']
#         password = request.POST['password']

#         user = auth.authenticate(email=email, password=password)

#         if user is not None and user.is_staff:
#             auth.login(request, user)
#             # return redirect('vaccineform')
#             return HttpResponseRedirect('https://yogeshiitm.github.io/TechHD-adminpanel/')

#         else:
#             messages.error(request, 'The email address provided is not registered as Vaccination Incharge please contact the site admin!')
#             return redirect('login')

#     else:
#         if request.user.is_authenticated:
#             # return redirect('vaccineform')
#             return HttpResponseRedirect('https://yogeshiitm.github.io/TechHD-adminpanel/')
#         else:
#             return render(request, 'accounts/login.html')


@login_required(login_url='login')
def vaccination_incharge(request):
    if request.method == 'POST':
        search = request.POST.get('search')
        if search is not None:

            arr1=search.split()
            arr2=[]
            for str in arr1:
                if str.lower() !='and':
                    arr2.append(str.capitalize())
                else:
                    arr2.append(str.lower())
            formattedSearch = ' '.join(arr2)

            try:
                state = StateModel.objects.get(state = formattedSearch)
                print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = formattedSearch)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('signup')


        str = request.POST['adhaar']
        adhaar = ''.join([str[:4], str[5:9], str[10:14], str[15:]])
        print(adhaar)
        #email = request.user.email
        name = request.user.first_name + ' ' + request.user.last_name
        #user = MedicalModel.objects.get(user=request.user)  
        users_search = MedicalModel.objects.filter(adhaar = adhaar)
        context={
            #'email':email,
            'name':name,
            #'user':user,
            'users_search':users_search,
        }
        return render(request, 'accounts/vaccinator.html',context)


    else:
        #email = request.user.email
        name = request.user.first_name + ' ' + request.user.last_name
        #user = MedicalModel.objects.get(user=request.user)  
        users = MedicalModel.objects.all()
        context={
            #'email':email,
            'name':name,
            #'user':user,
            'users':users,
        }
        return render(request, 'accounts/vaccinator.html',context)


@login_required(login_url='login')
def vaccination_profile(request, user_id):
    user = CustomUser.objects.get(id= user_id)
    user2 = MedicalModel.objects.get(user=user)
    str = user2.adhaar
    adhaar = '-'.join([str[:4], str[4:8], str[8:12], str[12:]])
    context = {
        'name': user.get_full_name(),
        'email': user.email,
        'adhaar': adhaar,
        'date1': datetime.datetime.today(),
        'date2': datetime.datetime.today() + datetime.timedelta(days=28)
    }
    return render(request, 'accounts/vaccination_profile.html', context)


# @login_required(login_url='login')
# def notify(request, user_id):
#     user = CustomUser.objects.get(pk=user_id)
#     user2 = MedicalModel.objects.get(user=user)
#     user2.vaccination_status = 'Alloted'
#     user2.save()
#     return redirect('vaccination_incharge')


@login_required(login_url='login')
def cross_off(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user2 = MedicalModel.objects.get(user=user)
    #print(user2.vaccination_status,'\n')
    user2.vaccination_status = 'Vaccinated'
    user2.save()
    #print(user2.vaccination_status,'\n')
    return redirect('vaccination_incharge')

@login_required(login_url='login')
def uncross(request, user_id):
    user = CustomUser.objects.get(pk=user_id)
    user2 = MedicalModel.objects.get(user=user)
    user2.vaccination_status = 'Alloted'
    user2.save()
    return redirect('vaccination_incharge')

