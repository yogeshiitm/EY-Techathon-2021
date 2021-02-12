import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.models import sequential

def Get_covid_state(url):
    r = requests.get(url, allow_redirects=True)
    open(f'time_series.csv', 'wb').write(r.content)


Get_covid_state('https://api.covid19india.org/csv/latest/states.csv')
data = pd.read_csv('time_series.csv', index_col=0)
data['Active'] = data.apply(lambda row: row.Confirmed - (row.Recovered + row.Deceased + row.Other), axis=1)

def run_NN_on_state(state):
    global data
    data = data[data['State'] == f'{state}']
    print(data.shape)
    train_data = data.iloc[:,6:7].values
    print(train_data)

    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(train_data)
    print(scaled_data)
    # state_data.drop(['Last_Updated_Time','State_code','Migrated_Other','Recovered','Migrated_Other','Delta_Confirmed','Delta_Recovered','Delta_Deaths','State_Notes'], axis='columns', inplace=True)

    x_train = []
    y_train = []

    for i in range(40,len(data)):
        x_train.append(scaled_data[i-40:i,0])
        y_train.append(scaled_data[i,0])
    
    x_train = np.array(x_train)
    y_train = np.array(y_train)

    print(x_train.shape)
    print(y_train.shape)

    x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

run_NN_on_state('Delhi')