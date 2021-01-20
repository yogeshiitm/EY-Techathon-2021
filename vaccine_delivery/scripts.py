import requests
import datetime
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn import preprocessing
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

class State_data:
    def __init__(self):
        pass 

    def Get_covid_district_wise(self,url):
        r = requests.get(url, allow_redirects=True)
        open(f'state_wise.csv', 'wb').write(r.content)

    def Get_trained_data(self,url):
        self.Get_covid_district_wise(url)
        state_data = pd.read_csv('state_wise.csv', index_col=0)
        state_data.drop(['Last_Updated_Time','State_code','Migrated_Other','Recovered','Migrated_Other','Delta_Confirmed','Delta_Recovered','Delta_Deaths','State_Notes'], axis='columns', inplace=True)
        other_data = pd.read_csv('state_data.csv', index_col=0)
        data = pd.merge(state_data,other_data,on = ['State'])
        data['Ratio_vacant_beds'] = data.apply(lambda row: row.Active/row.Hospital_beds, axis=1)
        data['Death_rate'] = data.apply(lambda row: (row.Deaths/row.Confirmed)*100, axis=1)
        return data

    def Get_clustered_data(self,url):
        data = self.Get_trained_data(url)
        features = data[['Active','Death_rate','Population_density','All_health_workers_percent','Senior_citizen','Children','Ratio_vacant_beds','Accessibility']]
        x = np.array(features).reshape(-1,8)
        x= preprocessing.StandardScaler().fit_transform(x)
        
        '''
        pca = PCA(n_components=8)
        pca.fit(x)
        variance = pca.explained_variance_ratio_ 
        var=np.cumsum(np.round(variance, 3)*100)
        plt.figure(figsize=(12,6))
        plt.ylabel('% Variance Explained')
        plt.xlabel('# of Features')
        plt.title('PCA Analysis')
        plt.ylim(0,100.5)
        plt.plot(var)
        plt.show()
        '''
        pca = PCA(n_components=3)
        pca.fit(x)
        pca_scale = pca.transform(x)

        Score = []
        labels=[]

        for no_of_clusters in range(2,34):
            KMean = KMeans(n_clusters=no_of_clusters)
            KMean.fit(pca_scale)
            label = KMean.predict(pca_scale)
            labels.append(label)
            silhouette = silhouette_score(pca_scale,label)
            Score.append(silhouette)

        Score_sort = sorted(Score)
        index = Score.index(Score_sort[len(Score_sort)-1])
        data['Clusters'] = pd.Series(labels[index], index=data.index)
        return data

    def Get_ranked_states(self,url):
        data = self.Get_clustered_data(url)
        no_of_clusters = len(data.Clusters.unique())

        S = []
        Repr = []
        data['Batch_no']= ''
        data['Further_percentage_no']=''

        for i in range(no_of_clusters):
            df = data[data['Clusters']==i]
            df_mean = df[['Active','All_health_workers_percent','Senior_citizen','Children','Death_rate','Ratio_vacant_beds','Population_density','Accessibility']]
            df_mean = df_mean.mean(axis=0)
            x = np.array(df_mean).reshape(-1,8)
            Repr.append(x)

        x = np.concatenate(Repr,axis=0)
        x = preprocessing.MinMaxScaler().fit_transform(x)

        for i in range(no_of_clusters):
            # S.append(0.395*(x[i][0])+0.275*(1-x[i][1])+0.176*(1-x[i][2])+0.1*(x[i][3])+0.044*(x[i][4])+0.01*(x[i][5]))
            # S.append(0.3089*(x[i][0])+0.2481*(x[i][1])+0.1899*(1-x[i][2])+0.1344*(x[i][3])+0.0826*(x[i][4])+0.03*(x[i][5]))
            #S.append(0.231*(x[i][0])+0.220*(x[i][1])+0.148*(x[i][2])+0.138*(x[i][3])+0.108*(x[i][4])+0.078*(x[i][5])+0.050*(x[i][6])+0.02*(x[i][7]))
            S.append(0.261*(x[i][0])+0.195*(x[i][1])+0.160*(x[i][2])+0.132*(x[i][3])+0.105*(x[i][4])+0.074*(x[i][5])+0.045*(x[i][6])+0.02*(x[i][7]))
            #S.append(0.313*(x[i][0])+0.230*(x[i][1])+0.186*(x[i][2])+0.122*(x[i][3])+0.078*(x[i][4])+0.044*(x[i][5])+0.019*(x[i][6])+0.004*(x[i][7]))
            #S.append(0.35*(x[i][0])+0.254*(x[i][1])+0.173*(x[i][2])+0.109*(x[i][3])+0.062*(x[i][4])+0.030*(x[i][5])+0.011*(x[i][6])+0.001*(x[i][7]))

        sort_S = sorted(S)
        for i in range(no_of_clusters):
            data.loc[data['Clusters'] == S.index(sort_S[i]), 'Batch_no'] = no_of_clusters-i

        data.drop(['Clusters'], axis='columns', inplace=True)

        frames=[0]*no_of_clusters
        #Repeat the same for each cluster n calculate S and attach percentage to it..
        for i in range(1,no_of_clusters+1):
            df = data[data['Batch_no']==i]
            
            if df.shape[0]<2:
                df['Further_percentage_no']= 100
                frames[i-1] = df
                continue

            x = df[['Active','Senior_citizen','All_health_workers_percent','Children','Death_rate','Ratio_vacant_beds','Population_density','Accessibility']]
            x = np.array(x).reshape(-1,8)
            x = preprocessing.MinMaxScaler().fit_transform(x)

            S = []
            #Rank Array    
            for j in range(df.shape[0]):
                # S.append(0.395*(x[j][0])+0.275*(1-x[j][1])+0.176*(1-x[j][2])+0.1*(x[j][3])+0.044*(x[j][4])+0.01*(x[j][5]))
                #S.append(0.3089*(x[j][0])+0.2481*(x[j][1])+0.1899*(1-x[j][2])+0.1344*(x[j][3])+0.0826*(x[j][4])+0.03*(x[j][5]))
                # S.append(0.231*(x[j][0])+0.200*(x[j][1])+0.168*(x[j][2])+0.138*(x[j][3])+0.108*(x[j][4])+0.078*(x[j][5])+0.050*(x[j][6])+0.02*(x[j][7]))
                S.append(0.313*(x[j][0])+0.240*(1-x[j][1])+0.176*(x[j][2])+0.122*(x[j][3])+0.078*(x[j][4])+0.044*(x[j][5])+0.019*(x[j][6])+0.004*(x[j][7]))
                #S.append(0.35*(x[j][0])+0.254*(1-x[j][1])+0.173*(x[j][2])+0.109*(x[j][3])+0.062*(x[j][4])+0.030*(x[j][5])+0.011*(x[j][6])+0.001*(x[j][7]))
            
            j=0
            for index in df.index:
                df.at[index, 'Further_percentage_no'] = (S[j]/sum(S))*100
                j=j+1
            
            frames[i-1] = df

        data = pd.concat(frames)
        data.to_csv('clustered_data.csv')
        #return data
    


class District_data:
    def __init__(self):
        pass 

    def Get_covid_district_wise(self,url):
        r = requests.get(url, allow_redirects=True)
        open(f'district_wise.csv', 'wb').write(r.content)

    def Get_train_data_on_districts(self,url):
        self.Get_covid_district_wise(url)

        district_data = pd.read_csv('district_wise.csv')
        district_data = district_data[district_data['Date'] == (datetime.datetime.today()-datetime.timedelta(days=1)).strftime('%Y-%m-%d')]
        district_data.loc[(district_data.District == 'Unknown'), 'District'] = district_data['State']
        district_data['Active'] = district_data['Confirmed']-(district_data['Recovered']+district_data['Deceased']+district_data['Other'])
        district_data.drop(['Confirmed','Recovered','Deceased','Other','Tested'], axis='columns', inplace=True)

        other_data = pd.read_csv('district_data.csv', index_col=0)
        data = pd.merge(district_data,other_data,on = ['State','District'])
        return data

    def Run_ML_on_state(self,state,data):
        data = data[data['State']== state]
        data['Clusters'] = ''

        if data.shape[0]>2:
            features = data[['Active','Population_2020']]
            x = np.array(features).reshape(-1,2)
            x= preprocessing.StandardScaler().fit_transform(x)

            Score = []
            Score_sort = []
            labels=[]

            for no_of_clusters in range(2,data.shape[0]):
                KMean = KMeans(n_clusters=no_of_clusters)
                KMean.fit(x)
                label = KMean.predict(x)
                silhouette = silhouette_score(x,label)
                Score.append(silhouette)
                labels.append(label)

            Score_sort = sorted(Score)
            index = Score.index(Score_sort[len(Score_sort)-1])

            data['Clusters'] = pd.Series(labels[index], index=data.index)
            #data.to_csv(f'State_Clusters\clustered_data_{state}.csv')
            return data
        
        else:
            data['Clusters'] = 1
            return data

    def Get_rank_on_clusters(self,state, data):
        data = data[data['State'] == state]
        no_of_clusters = len(data.Clusters.unique())
        
        if no_of_clusters<2:
            data['Batch_no']= 1
            data.drop(['Clusters'], axis='columns', inplace=True)
            return data

        S = []
        Repr = []
        data['Batch_no']= ''

        for i in range(no_of_clusters):
            df = data[data['Clusters']==i]
            df_mean = df[['Active','Population_2020']]
            df_mean = df_mean.mean(axis=0)
            x = np.array(df_mean).reshape(-1,2)
            Repr.append(x)

        x = np.concatenate(Repr,axis=0)
        x = preprocessing.MinMaxScaler().fit_transform(x)

        for i in range(no_of_clusters):
            S.append(0.66*(x[i][0])+0.34*(x[i][1]))

        sort_S = sorted(S)
        for i in range(no_of_clusters):
            data.loc[data['Clusters'] == S.index(sort_S[i]), 'Batch_no'] = no_of_clusters-i

        data.drop(['Clusters'], axis='columns', inplace=True)
        return data


    def Get_clustered_data(self,url):
        data = self.Get_train_data_on_districts(url)
        states = data.State.unique()
        frames=[0]*len(states)

        for i in range(len(states)):
            frames[i] = self.Run_ML_on_state(states[i],data)

        data = pd.concat(frames)
        return data


    def Get_ranked_districts(self,url):
        data = self.Get_clustered_data(url)
        states = data.State.unique()
        frames=[0]*len(states)

        for i in range(len(states)):
            frames[i] = self.Get_rank_on_clusters(states[i],data)

        data = pd.concat(frames)
        data.to_csv('clustered_data_district.csv')
        #return data
