import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import LSTM
from keras.models import Sequential
import matplotlib.pyplot as plt

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
    # train_data.to_csv('train_data.csv')
    plt.plot(train_data)
    plt.show()

    scaler = MinMaxScaler(feature_range=(0,1))
    scaled_data = scaler.fit_transform(train_data)
    print(scaled_data)
    # state_data.drop(['Last_Updated_Time','State_code','Migrated_Other','Recovered','Migrated_Other','Delta_Confirmed','Delta_Recovered','Delta_Deaths','State_Notes'], axis='columns', inplace=True)

    x_train = []
    y_train = []

    for i in range(8,len(data)):
        x_train.append(scaled_data[i-8:i,0])
        y_train.append(scaled_data[i,0])
    
    x_train = np.array(x_train)
    y_train = np.array(y_train)

    print(x_train.shape)
    print(y_train.shape)

    x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))

    #LSTM architecture
    model = Sequential()
    model.add(LSTM(units = 100, return_sequences = True, input_shape =(x_train.shape[1],1)))
    model.add(Dropout(0.5))
    model.add(LSTM(units = 50, return_sequences = True))
    model.add(Dropout(0.3))
    model.add(LSTM(units =50))
    modek.add(Dropout(0.3))
    mdoel.add(Dense(units=100))

    model.compule(optimizer='adam', loss='mean_squared_error')
    model.fit(x_train,y_train,epochs=100,batch_size=20)

    x_test = []
    n = len(data)
    for i in range(28):
        x_test = []
        x_test = scaled_data[(n+i)-10:(n+i),0]
        x_test = np.reshape(x_test, (x_test.shape[0],x_test.shape[1],1))
        prediction = x_



run_NN_on_state('Delhi')