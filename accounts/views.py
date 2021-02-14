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
from .scripts import get_list


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

            if request.POST.get('RegistrarLogin')== 'True':
                if user is not None and user.is_staff:
                    auth.login(request, user)

                    return redirect('registrar')

                else:
                    messages.error(request, 'The email address provided is not registered as Registrar please contact the site admin!')
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
        occupation = request.POST.get('occupation')
        income = request.POST.get('income')
        work_status = int(request.POST.get('work_status'))
        
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

        detail = MedicalModel(user = user,adhaar = adhaar,mobile = mobile,pincode=pincode,occupation=occupation,income=income,work_status=work_status,state=state,district=district,age=age,gender=gender,covid=covid,smoker=smoker,hbp_hyt=hbp_hyt,respiratory=respiratory,chd=chd,diabetes=diabetes,cancer_non=cancer_non,hmt=hmt,reduced_kidney=reduced_kidney,kidney_dialysis=kidney_dialysis,liver_disease=liver_disease,strk_dmtia=strk_dmtia,other_neuro=other_neuro,organ_transplant=organ_transplant)
        detail.save()
        detail.get_illness_no()
        detail.set_medical_eligibility()
        detail.set_economy_eligibility()
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
        phase = int(request.POST.get('phase'))
        # print(phase,'hello')
        email = request.user.email
        name = request.user.first_name + ' ' + request.user.last_name

        states = StateModel.objects.all().order_by('state')
        users = get_list(phase,state,district)

        try:
            #user = MedicalModel.objects.get(user=request.user)  
            context={
                # 'email':email,
                # 'name':name,
                # 'user':user,
                'users':users,
                'states':states,
                'current_state': request.POST.get('state'),
                'current_district': request.POST.get('district'),
                'no_vaccines': int(request.POST.get('vaccine')),
                'current_phase': int(request.POST.get('phase'))
            }

        except MedicalModel.DoesNotExist:
            context={
                'states':states,
                'users':users,
                'current_state': request.POST.get('state'),
                'current_district': request.POST.get('district'),
                'no_vaccines': int(request.POST.get('vaccine')),
                'current_phase': int(request.POST.get('phase'))
            }

        if request.POST.get('SearchUsers')== 'True':
            return render(request, 'accounts/health_admin.html',context)

        elif request.POST.get('NotifyUsers')== 'True':
            users_available = False
            for user2 in users:
                if user2.vaccination_status == '':
                    users_available = True

                if not user2.vaccination_status == 'Vaccinated':
                    user2.vaccination_status = 'Alloted'
                    user2.save()
            
            print(users_available,'\n')
            print(users_available == True,'\n')
            if users_available == True:
                messages.success(request, "Beneficiaries notified !!!")
            else:
                messages.error(request, "No beneficiary available in Phase {}".format(int(request.POST.get('phase'))))
            return render(request, 'accounts/health_admin.html',context)


    else:
        if request.user.is_staff:

            # states = StateModel.objects.all().order_by('state')
            # email = request.user.email
            # name = request.user.first_name + ' ' + request.user.last_name
            # return render(request, 'accounts/health_admin.html',{'name':name,'email':email, 'states':states})

            try:
                states = StateModel.objects.all().order_by('state')
                #email = request.user.email
                name = request.user.first_name + ' ' + request.user.last_name
                #user = MedicalModel.objects.get(user=request.user)  
                context={
                    #'email':email,
                    'name':name,
                    #'user':user,
                    'states':states
                }
                return render(request, 'accounts/health_admin.html',context)

            except MedicalModel.DoesNotExist:
                states = StateModel.objects.all().order_by('state')
                #email = request.user.email
                name = request.user.first_name + ' ' + request.user.last_name
                #user = MedicalModel.objects.get(user=request.user)  
                context={
                    #'email':email,
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
                #print(state)
                return redirect(f'/district_level/{state.state}')
            
            except StateModel.DoesNotExist:
                try :
                    district = DistrictModel.objects.get(district = formattedSearch)
                    return redirect(f'/district_level/{district.state}')
                except DistrictModel.DoesNotExist:
                    return redirect('signup')


        if request.POST.get('SearchUser')== 'True':
            str = request.POST['adhaar']
            adhaar = ''.join([str[:4], str[5:9], str[10:14], str[15:]])
            #print(adhaar)
            #email = request.user.email
            name = request.user.first_name + ' ' + request.user.last_name
            #user = MedicalModel.objects.get(user=request.user)  
            users_search = MedicalModel.objects.filter(adhaar = adhaar)
            context={
                #'email':email,
                'name':name,
                #'user':user,
                'users_search':users_search,
                'button_name': 'SearchUser'
            }
            return render(request, 'accounts/vaccination_incharge.html',context)


        if request.POST.get('ResetUsers')== 'True':
            users = MedicalModel.objects.all()
            for user in users:
                if user.vaccination_status == 'Alloted':
                    user.vaccination_status = ''
                    user.save()

            #email = request.user.email
            name = request.user.first_name + ' ' + request.user.last_name
            #user = MedicalModel.objects.get(user=request.user)  
            
            atleast_one_vaccinated = False
            for user in users:
                if user.vaccination_status == 'Vaccinated':
                    atleast_one_vaccinated = True

            context={
                #'email':email,
                'name':name,
                #'user':user,
                'users':users,
                'atleast_one_alloted': False,
                'atleast_one_vaccinated': atleast_one_vaccinated,
                'button': 'ResetUsers'
            }
            return render(request, 'accounts/vaccination_incharge.html',context)


    else:
        #email = request.user.email
        name = request.user.first_name + ' ' + request.user.last_name
        #user = MedicalModel.objects.get(user=request.user)  
        users = MedicalModel.objects.all()

        atleast_one_alloted = False
        atleast_one_vaccinated = False
        for user in users:
            if user.vaccination_status == 'Alloted':
                atleast_one_alloted = True

            if user.vaccination_status == 'Vaccinated':
                atleast_one_vaccinated = True

        context={
            #'email':email,
            'name':name,
            #'user':user,
            'users':users,
            'atleast_one_alloted': atleast_one_alloted,
            'atleast_one_vaccinated': atleast_one_vaccinated
        }
        return render(request, 'accounts/vaccination_incharge.html',context)


@login_required(login_url='login')
def vaccination_profile(request, user_id):
    if request.method == 'POST':

        user = CustomUser.objects.get(id= user_id)
        user2 = MedicalModel.objects.get(user=user)

        user2.dose_status = 0
        if request.POST.get('2nd_vaccine',0) == '2':
            user2.dose_status = 2
        elif request.POST.get('1st_vaccine',0) == '1':
            user2.dose_status = 1
            user2.vaccination_status

        user2.vaccine_name = request.POST['vaccinename']
        user2.save()
        return redirect('vaccination_incharge')


    else:
        user = CustomUser.objects.get(id= user_id)
        user2 = MedicalModel.objects.get(user=user)
        #print(str(datetime.datetime.today()))

        if user2.date1 == None:
            #user2.date1= datetime.datetime.today().strftime("%Y-%m-%d")
            user2.date1= datetime.datetime.today().date()
            #user2.date2= (datetime.datetime.today()+ datetime.timedelta(days=28)).strftime("%Y-%m-%d")
            user2.date2= (datetime.datetime.today()+ datetime.timedelta(days=28)).date()
            user2.save()
        
        print('date2\n',user2.date2)

        str = user2.adhaar
        adhaar = '-'.join([str[:4], str[4:8], str[8:12], str[12:]])
        context = {
            'name': user.get_full_name(),
            'email': user.email,
            'user' : user2,
            'adhaar': adhaar,
        }
        return render(request, 'accounts/vaccination_profile.html', context)


#to convert vaccination status from '' to 'alloted'
@login_required(login_url='login')
def cross_off(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user2 = MedicalModel.objects.get(user=user)
    #print(user2.vaccination_status,'\n')
    if user2.vaccination_status == '':
        user2.vaccination_status = 'Alloted'
        user2.save()
        print(user2.vaccination_status,'\n')
        return redirect('healthadmin')
    elif user2.vaccination_status == 'Alloted':
        user2.vaccination_status = 'Vaccinated'
        user2.save()
        print(user2.vaccination_status,'\n')
        return redirect('vaccination_incharge')


#to convert vaccination status from 'vaccinated' to ''
@login_required(login_url='login')
def uncross(request, user_id):
    user = CustomUser.objects.get(pk=user_id)
    user2 = MedicalModel.objects.get(user=user)
    if user2.vaccination_status == 'Alloted':
        user2.date1=None
        user2.date2=None
        user2.dose_status = 0
        user2.vaccine_name = ''
        user2.vaccination_status = ''
        user2.save()
        print(user2.vaccination_status,'\n')
        return redirect('healthadmin')
    elif user2.vaccination_status == 'Vaccinated':
        user2.date1=None
        user2.date2=None
        user2.dose_status = 0
        user2.vaccine_name = ''
        user2.vaccination_status = 'Alloted'
        user2.save()
        print(user2.vaccination_status,'\n')
        return redirect('vaccination_incharge')


def registrar(request):
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
                form = CustomRegisterForm()
                users = CustomUser.objects.all().order_by('-date_joined')[:5]
                context={
                    'email':email,
                    'name':name,
                    'user':user,
                    'states':states,
                    'form':form,
                    'users':users
                }
                return render(request, 'accounts/registrar.html',context)

            except MedicalModel.DoesNotExist:
                states = StateModel.objects.all().order_by('state')
                email = request.user.email
                name = request.user.first_name + ' ' + request.user.last_name
                #user = MedicalModel.objects.get(user=request.user)
                form = CustomRegisterForm()
                users = CustomUser.objects.all().order_by('-date_joined')[:5]
                context={
                    'email':email,
                    'name':name,
                    #'user':user,
                    'states':states,
                    'form':form,
                    'users':users
                }
                return render(request, 'accounts/registrar.html',context)

        else:
            #return redirect('dashboard')
            messages.error(request, 'The email address provided is not registered as a Registrar please contact the site admin!')
            return render(request, 'accounts/login.html')
    
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
                    return redirect('registrar')

        #category = int(request.POST.get('category'))
        #age = request.POST.get('age')

        # list = re["fullname"].split()
        # firstname = list[0]
        # lastname = ' '.join(list[1:])

        # user.first_name = firstname.capitalize()
        # user.last_name = lastname.capitalize()
        # user.email = self.cleaned_data["email"]
        # user.save()

        states = StateModel.objects.all().order_by('state')

        form = CustomRegisterForm(request.POST or None)
        # form.password1 = 'Registrar@123'
        # form.password2 = 'Registrar@123'

        if form.is_valid():

            form.save()

            user = CustomUser.objects.get(email = form.cleaned_data['email'])
            user.is_active = True
            
            adhaar = request.POST.get('adhaar')
            mobile = request.POST.get('mobile')
            pincode = request.POST.get('pincode')
            occupation = request.POST.get('occupation')
            state = request.POST.get('state')
            district = request.POST.get('district')
            age = request.POST.get('dob')
            gender = request.POST.get('gender')
            occupation = request.POST.get('occupation')
            income = request.POST.get('income')
            work_status = int(request.POST.get('work_status'))
            
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

            detail = MedicalModel(user = user,adhaar = adhaar,mobile = mobile,pincode=pincode,occupation=occupation,income=income,work_status=work_status,state=state,district=district,age=age,gender=gender,covid=covid,smoker=smoker,hbp_hyt=hbp_hyt,respiratory=respiratory,chd=chd,diabetes=diabetes,cancer_non=cancer_non,hmt=hmt,reduced_kidney=reduced_kidney,kidney_dialysis=kidney_dialysis,liver_disease=liver_disease,strk_dmtia=strk_dmtia,other_neuro=other_neuro,organ_transplant=organ_transplant)
            detail.save()
            detail.get_illness_no()
            detail.set_medical_eligibility()
            detail.set_economy_eligibility()

            users = CustomUser.objects.all().order_by('-date_joined')[:5]

            try:
                user = MedicalModel.objects.get(user=request.user)  
                context={
                    'email':user.user.email,
                    'name':user.user.first_name + ' ' + user.user.last_name,
                    'user':user,
                    'users':users,
                    'states':states,
                    'form':form
                }

            except MedicalModel.DoesNotExist:
                #user = MedicalModel.objects.get(user=request.user)
                email = request.user.email
                name = request.user.first_name + ' ' + request.user.last_name
                context={
                    'email':email,
                    'name':name,
                    'users':users,
                    'states':states,
                    'form' : form,
                    'users':users
                }

            return render(request, 'accounts/registrar.html' , context)

            # auto login after signup
            # https://stackoverflow.com/a/39316967/13962648
            # auth_login(request, user)
            # return redirect('vaccineform')

        else:
            messages.error(request, form.errors)
            users = CustomUser.objects.all().order_by('-date_joined')[:5]
            try:
                user = MedicalModel.objects.get(user=request.user)  
                context={
                    'email':user.user.email,
                    'name':user.user.first_name + ' ' + user.user.last_name,
                    'users':users,
                    'states':states,
                    'form':form
                }

            except MedicalModel.DoesNotExist:
                #user = MedicalModel.objects.get(user=request.user)
                email = request.user.email
                name = request.user.first_name + ' ' + request.user.last_name
                context={
                    'email':email,
                    'name':name,
                    'states':states,
                    'form' : form,
                    'users': users
                }
            return render(request, 'accounts/registrar.html' , context)