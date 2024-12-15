import torch
import torch.nn as nn
import yfinance as yf
import pandas as pd
import numpy as np
# import enchant
# from newsapi import NewsApiClient
import datetime
from datetime import datetime, timedelta
from transformers import pipeline
import requests
from bs4 import BeautifulSoup
import datetime
from glob import glob
import pandas as pd
import matplotlib.pyplot as plt
# api = open("/home/kl/github/Uwu/api.txt", "r").readline()



def drop_zero_column(df0):
    return df0.loc[:,(df0 != 0).any(axis=0)]

def expand_news(df1,df2,noise=True):
    
    """
    Expand df2 to size of df 1
    :params
        df1 - first dataframe, forex tick object, Ex // forex.day or forex.min
        df2 - the read_csv(path) of the file
        -> Note requires the format [Datetime, Text, ...., n]
            where n is however many labels desired

    :out
        news_vec - numpy array of new entry column for news

    """
    assert type(df1) == pd.DataFrame, "First entry not Pandas"
    # assert type(df2) == pd.DataFrame, "Second entry not Pandas"

    # df2 = pd.read_csv(df2_file)
    # print(df2)
    labels = df2.iloc[:,2:]
    dates = df2.iloc[:,0].to_numpy()
    news_vec = np.zeros((len(df1),len(df2.columns)-2))

    # Remove and uncomment line below this to make work
    if noise:
        news_vec = np.random.randn(len(df1),len(df2.columns)-2) / 9
        # news_vec = np.zeros((len(df1),len(df2.columns)-2))

    count = 0
    count_max = len(df2) -1
    

    # print(labels[df2.columns[0+2]])
    # return 
    for col in range(len(labels.columns)):
        for i in range(0,len(news_vec)):
            
            if (df1.iloc[i,0] > dates[count] and count < count_max):
                count += 1
            news_vec[i,col] = labels.iloc[count,col]

    return pd.DataFrame(news_vec)



def get_data(x):
    x_train = x[["Datetime", "Open"]].to_numpy()[:int(len(x)*0.8)]
    x_train = torch.tensor(x_train, dtype=torch.double)

    y_train = x[["High"]].to_numpy(dtype=np.double)[:int(len(x)*0.8)]
    y_train = torch.tensor(y_train, dtype=torch.double)

    x_test = x[["Datetime", "Open"]].to_numpy()[int(len(x)*0.8):]
    x_test = torch.tensor(x_test, dtype=torch.double)

    y_test = x[["High"]].to_numpy()[int(len(x)*0.8):]
    y_test = torch.tensor(y_test, dtype=torch.double)

    if torch.cuda.is_available():
        return x_train.cuda(), y_train.cuda(), x_test.cuda(), y_test.cuda()
    else:
        return x_train, y_train, x_test, y_test

def get_day(tick):
    data = yf.download(tick, interval= "1d", period = "max",progress=False, ignore_tz=True).reset_index()
    data.rename(columns={"Date":"Datetime"},inplace=True)
    data.Datetime  = data.Datetime.apply(lambda x: x.timestamp())
    return data.iloc[:,0:6]

def get_hr(tick):
    data = yf.download(tick, interval= "1h", period = "730d",progress=False, ignore_tz=True).reset_index()
    data.Datetime = data.Datetime.apply(lambda x: x.timestamp())
    return data.iloc[:,0:6]

def get_min(tick, all_days=False): 
    if (all_days):
        t = datetime.datetime.today() - timedelta(days=29)
        initial = yf.download(tick, interval= "1m", start = t, end = t + timedelta(days=5) ,progress=False, ignore_tz=True).reset_index()
        t += timedelta(days=5)

        while (t < datetime.datetime.today()):
            i2 = yf.download(tick, interval= "1m", start = t, end = t + timedelta(days=5) ,progress=False, ignore_tz=True).reset_index()
            t += timedelta(days=5)
            initial = pd.concat([initial,i2], axis = 0)

        initial.drop_duplicates(inplace=True)
        initial.Datetime = initial.Datetime.apply(lambda x: x.timestamp())
        return initial

    else:
        data = yf.download(tick, interval= "1m", period = "max",progress=False, ignore_tz=True).reset_index()
    data.Datetime = data.Datetime.apply(lambda x: x.timestamp())
    return data.iloc[:,0:6]

def best_action(arr, n,view=False,arr2d=False,expand=True):

    """
    Function to mathamatically guess most optimal buy/sell action at a given point.

    :params

        arr - the array to create the best decisions 
        n - nodes, higher nodes means sparser decisions and vice versa
    
        view - This is to just view the decisions comapred to actual. True prints graph
    :out
        barr - the best decision at given points. 1 = buy, -1 = sell, 0 = none

    """

    if (type(arr) == pd.DataFrame):
        arr = arr.iloc[:,5].to_numpy()

    a = 0
    b = len(arr)

    darr = [arr[i] for i in range(a,b, n)]
    

    farr = np.zeros(len(darr))

    for i in range(0,len(farr)-1):
        if darr[i-1] < darr[i] and darr[i] > darr[i+1]:
            farr[i] = -1
        elif darr[i-1] > darr[i] and darr[i] < darr[i+1]:
            farr[i] = 1
        else:
            farr[i] = 0
        

    if arr2d:
        barr = np.zeros((len(arr),3))
    
        for i in range(0,len(darr)):
            if (farr[i] <= -0.5):
                barr[i*n][0] = 1
            elif farr[i] >= 0.5:
                barr[i*n][2] = 1
            else:
                barr[i*n][1] = 1

        for i in range(0,len(barr)):
            if (abs(barr[i].sum()) <= 0.4):
                barr[i][1] = 1
            

    else:
        barr = np.zeros(len(arr))
        
        for i in range(0,len(darr)):
            barr[i*n] = farr[i]
                  
    if (view):
        plt.plot(arr, "blue", barr * abs(arr.max() - arr.min()) + arr.mean(), "g--")


    return barr  # * abs(arr.max() - arr.min()) + arr.mean()


