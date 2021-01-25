from django.shortcuts import render, redirect
from .models import *
from datetime import datetime,timedelta
from .scripts import State_data, District_data
import pandas as pd
import datetime
import pytz
from .forms import SearchForm
from django.contrib import messages, auth

def State_data_update():
    data = State_data()
    data.Get_ranked_states(url='https://api.covid19india.org/csv/latest/state_wise.csv')
    #data = states_data.Get_ranked_states(url='https://api.covid19india.org/csv/latest/state_wise.csv')
    data = pd.read_csv('clustered_data.csv',sep=',')
    row_iter = data.iterrows()
    StateModel.objects.all().delete()
    STATES = [
            StateModel(
                state = row['State'],
                active = row['Active'],
                population_2020 = row['Population_density'],
                accessibility = row['Accessibility'],
                children = row['Children'],
                senior_citizen = row['Senior_citizen'],
                all_health_workers_percent = row['All_health_workers_percent'],
                death_rate = row['Death_rate'],
                ratio_vacant_beds = row['Ratio_vacant_beds'],
                batch_no = row['Batch_no'],
                percentage_vaccine_delivery = row['Further_percentage_no'],
                )
                for index, row in row_iter
    ]
    StateModel.objects.bulk_create(STATES)

    data = pd.read_csv('clustered_data.csv')
    data = data[['Code','Active']]
    # data.drop(['State'])
    data.to_csv('static/files/active_map.csv', index = False)
    data.to_csv('assets/files/active_map.csv', index = False)

    data = pd.read_csv('clustered_data.csv')
    data = data[['Code','Batch_no']]
    # data.drop(['State'])
    data.to_csv('static/files/batch_map.csv', index=False)
    data.to_csv('assets/files/batch_map.csv', index=False)


def District_data_update():
    data = District_data()
    data.Get_ranked_districts(url ='https://api.covid19india.org/csv/latest/districts.csv')

    data = pd.read_csv('clustered_data_district.csv', index_col=0,sep=',')
    # maps = data[['State']]
    row_iter =data.iterrows()
    DistrictModel.objects.all().delete()
    DISTRICTS = [
            DistrictModel(
                state = row['State'],
                district = row['District'],
                active = row['Active'],
                population_2020 = row['Population_2020'],
                batch_no = row['Batch_no'],
                )
                for index, row in row_iter
    ]
    DistrictModel.objects.bulk_create(DISTRICTS)

'''
def Update_datasets(request):
    last_updated = request.session.get('last_updated')

    if last_updated is None:
        State_data_update()
        District_data_update()
        request.session['last_updated'] = date.today().strftime('%d-%m-%Y')

    elif last_updated != date.today().strftime('%d-%m-%Y'):
        State_data_update()
        District_data_update()
        request.session['last_updated'] = date.today().strftime('%d-%m-%Y')

    elif last_updated == date.today().strftime('%d-%m-%Y'):
        pass
'''

def check_update_time(request):
    global updated
    global date_file

    global top
    global confirmed
    global active
    global recovered
    global deaths

    date_file = open("updated_date.txt", "r")
    print(date_file)
    last_updated_date = date_file.readline()
    print(last_updated_date)
    print("Check_updated_date function called")
    tz = pytz.timezone('Asia/Kolkata')
    now_time = datetime.datetime.now(tz)
    if last_updated_date < str(now_time.strftime('%Y-%m-%d')):
        print("Last update time is old")
        print(now_time.hour)
        if 1 <= now_time.hour:
            print("Last updated Date is old. Fetching new Data..")
            State_data_update()
            print("State Data Updated! Now updating District Data..")
            District_data_update()
            print("District Data Updated!")
            date_file_write = open("updated_date.txt", "w")
            date_file_write.write(now_time.strftime('%Y-%m-%d'))
            print(last_updated_date)


# Create your views here.
def Index(request):

    if request.method == 'POST':
        form = SearchForm(request.POST)
        states = request.POST.get('search')
        try:
            state = StateModel.objects.get(state = states.capitalize())
            print(state)
            return redirect(f'/district_level/{state.state}')
            
        except StateModel.DoesNotExist:
            try :
                district = DistrictModel.objects.get(district = states.capitalize())
                return redirect(f'/district_level/{district.state}')
            except DistrictModel.DoesNotExist:
                return redirect('/')

    print("Request at / base path ")
    check_update_time(request)
    print("Checked updated with time")

    top = pd.read_csv('state_wise.csv',sep=',')
    top = top[top['State']=='Total']
    confirmed = int(top['Confirmed'])
    active = int(top['Active'])
    recovered = int(top['Recovered'])
    deaths = int(top['Deaths'])

    data = StateModel.objects.all().order_by('batch_no','-percentage_vaccine_delivery')
    form =SearchForm()

    context = {
        'data':data,
        'confirmed' : confirmed,
        'active' : active,
        'recovered' : recovered,
        'deaths' : deaths,
        'form':form
    }
    return render(request, "vaccine_delivery/index.html", context)


def StateMapView(request):
    check_update_time(request)
    return render(request, 'state_vaccine_delivery/map.html')


def DistrictHomeView(request):

    if request.method == 'POST':
        form = SearchForm(request.POST)
        states = request.POST.get('search')
        try:
            state = StateModel.objects.get(state = states.capitalize())
            print(state)
            return redirect(f'/district_level/{state.state}')
        except StateModel.DoesNotExist:
            try :
                district = DistrictModel.objects.get(district = states.capitalize())
                return redirect(f'/district_level/{district.state}')
            except DistrictModel.DoesNotExist:
                return redirect('/district_level')

    check_update_time(request)
    states = StateModel.objects.all().order_by('state')
    form = SearchForm()
    return render(request,'vaccine_delivery/district_level.html',{'states':states,'form':form})


def DistrictView(request, state):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        states = request.POST.get('search')
        try:
            state = StateModel.objects.get(state = states.capitalize())
            print(state)
            return redirect(f'/district_level/{state.state}')
        except StateModel.DoesNotExist:
            try :
                district = DistrictModel.objects.get(district = states.capitalize())
                return redirect(f'/district_level/{district.state}')
            except DistrictModel.DoesNotExist:
                return redirect(f'/district_level/{state}')

    check_update_time(request)
    data = DistrictModel.objects.filter(state = state).order_by('batch_no','-active','-population_2020')
    form = SearchForm()
    return render(request, 'vaccine_delivery/district_level_state.html', {'data': data,'form': form})


def BatchView(request, batch):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        states = request.POST.get('search')
        try:
            state = StateModel.objects.get(state = states.capitalize())
            print(state)
            return redirect(f'/district_level/{state.state}')
        except StateModel.DoesNotExist:
            try :
                district = DistrictModel.objects.get(district = states.capitalize())
                return redirect(f'/district_level/{district.state}')
            except DistrictModel.DoesNotExist:
                return redirect(f'/batch/{batch}')

    check_update_time(request)
    #Update_datasets(request)
    data = StateModel.objects.filter(batch_no = batch).order_by('-percentage_vaccine_delivery')
    top = pd.read_csv('clustered_data.csv',index_col=0)
    top = top.Batch_no.unique()
    form = SearchForm()
    return render(request, 'vaccine_delivery/batch.html', {'data': data, 'top':top, 'currentbatch': int(batch), 'form': form})


def AboutView(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        states = request.POST.get('search')
        try:
            state = StateModel.objects.get(state = states.capitalize())
            print(state)
            return redirect(f'/district_level/{state.state}')
        except StateModel.DoesNotExist:
            try :
                district = DistrictModel.objects.get(district = states.capitalize())
                return redirect(f'/district_level/{district.state}')
            except DistrictModel.DoesNotExist:
                return redirect('/about')
    
    form = SearchForm()
    return render(request,'vaccine_delivery/about.html',{'form':form})


def TeamView(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        states = request.POST.get('search')
        try:
            state = StateModel.objects.get(state = states.capitalize())
            print(state)
            return redirect(f'/district_level/{state.state}')
        except StateModel.DoesNotExist:
            try :
                district = DistrictModel.objects.get(district = states.capitalize())
                return redirect(f'/district_level/{district.state}')
            except DistrictModel.DoesNotExist:
                return redirect('/team')

    form = SearchForm()
    return render(request,'vaccine_delivery/team.html',{'form':form})
