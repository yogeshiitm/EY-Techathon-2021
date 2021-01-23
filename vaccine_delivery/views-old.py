from django.shortcuts import render, redirect
from .models import *
from datetime import datetime,timedelta
from .scripts import State_data, District_data
import pandas as pd


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


# Create your views here.
def Index(request):
    try:
        top = pd.read_csv('clustered_data.csv',sep=',')
        top = pd.read_csv('clustered_data_district.csv',sep=',')
        if len(top[top['Date']==(datetime.today()-timedelta(days=2)).strftime('%Y-%m-%d')]):
            State_data_update()
            District_data_update()
    except:
        State_data_update()
        District_data_update()
    
    finally:
        top = pd.read_csv('state_wise.csv',sep=',')
        top = top[top['State']=='Total']
        confirmed = int(top['Confirmed'])
        active = int(top['Active'])
        recovered = int(top['Recovered'])
        deaths = int(top['Deaths'])

        data = StateModel.objects.all().order_by('batch_no','-percentage_vaccine_delivery')

        context = {
            'data':data,
            'confirmed' : confirmed,
            'active' : active,
            'recovered' : recovered,
            'deaths' : deaths
        }
        return render(request, "vaccine_delivery/index.html", context)

def StateMapView(request):
    try:
        top = pd.read_csv('clustered_data.csv',sep=',')
        top = pd.read_csv('clustered_data_district.csv',sep=',')
        if len(top[top['Date']==(datetime.today()-timedelta(days=2)).strftime('%Y-%m-%d')]):
            State_data_update()
            District_data_update()
    except:
        State_data_update()
        District_data_update()

    finally:
        return render(request, 'state_vaccine_delivery/map.html')

def DistrictHomeView(request):
    try:
        top = pd.read_csv('clustered_data.csv',sep=',')
        top = pd.read_csv('clustered_data_district.csv',sep=',')
        if len(top[top['Date']==(datetime.today()-timedelta(days=2)).strftime('%Y-%m-%d')]):
            State_data_update()
            District_data_update()
    except:
        State_data_update()
        District_data_update()
    
    finally:
        states = StateModel.objects.all().order_by('state')
        return render(request,'vaccine_delivery/district_level.html',{'states':states})


def DistrictView(request, state):
    try:
        top = pd.read_csv('clustered_data.csv',sep=',')
        top = pd.read_csv('clustered_data_district.csv',sep=',')
        if len(top[top['Date']==(datetime.today()-timedelta(days=2)).strftime('%Y-%m-%d')]):
            State_data_update()
            District_data_update()
    except:
        State_data_update()
        District_data_update()

    finally:
        data = DistrictModel.objects.filter(state = state).order_by('batch_no','-active','-population_2020')
        return render(request, 'vaccine_delivery/district_level_state.html', {'data': data})

def BatchView(request, batch):
    try: 
        top = pd.read_csv('clustered_data.csv',sep=',')
        top = pd.read_csv('clustered_data_district.csv',sep=',')
        if len(top[top['Date']==(datetime.today()-timedelta(days=2)).strftime('%Y-%m-%d')]):
            State_data_update()
            District_data_update()
    except:
        State_data_update()
        District_data_update()
    
    finally:
        #Update_datasets(request)
        data = StateModel.objects.filter(batch_no = batch).order_by('-percentage_vaccine_delivery')
        top = pd.read_csv('clustered_data.csv',index_col=0)
        top = top.Batch_no.unique()
        
        return render(request, 'vaccine_delivery/batch.html', {'data': data, 'top':top, 'currentbatch': int(batch)})

def AboutView(request):
    return render(request,'vaccine_delivery/about.html')

def TeamView(request):
    return render(request,'vaccine_delivery/team.html')

