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


# Note, Does not use PATH




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

def get_day(pair):
    pair = pair+"=X"
    data = yf.download(pair, interval= "1d", period = "max",progress=False, ignore_tz=True).reset_index()
    data.rename(columns={"Date":"Datetime"},inplace=True)
    data.Datetime  = data.Datetime.apply(lambda x: x.timestamp())
    return data.iloc[:,0:6]

def get_hr(pair):
    pair = pair+"=X"
    data = yf.download(pair, interval= "1h", period = "730d",progress=False, ignore_tz=True).reset_index()
    data.Datetime = data.Datetime.apply(lambda x: x.timestamp())
    return data.iloc[:,0:6]

def get_min(pair, all_days=False):
    pair = pair+"=X"  
    if (all_days):
        t = datetime.datetime.today() - timedelta(days=29)
        initial = yf.download(pair, interval= "1m", start = t, end = t + timedelta(days=5) ,progress=False, ignore_tz=True).reset_index()
        t += timedelta(days=5)

        while (t < datetime.datetime.today()):
            i2 = yf.download(pair, interval= "1m", start = t, end = t + timedelta(days=5) ,progress=False, ignore_tz=True).reset_index()
            t += timedelta(days=5)
            initial = pd.concat([initial,i2], axis = 0)

        initial.drop_duplicates(inplace=True)
        initial.Datetime = initial.Datetime.apply(lambda x: x.timestamp())
        return initial

    else:
        data = yf.download(pair, interval= "1m", period = "max",progress=False, ignore_tz=True).reset_index()
    data.Datetime = data.Datetime.apply(lambda x: x.timestamp())
    return data.iloc[:,0:6]

def best_action(arr, n,view=False):

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

    barr = np.zeros(len(arr))
    
    for i in range(0,len(darr)):
        barr[i*n] = farr[i]
        
    if (view):
        plt.plot(arr, "blue", barr * abs(arr.max() - arr.min()) + arr.mean(), "g--")


    return barr  # * abs(arr.max() - arr.min()) + arr.mean()