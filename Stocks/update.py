import yfinance as yf
import pandas as pd
import numpy as np
from utils import *
from news_grabber import * 
import os
import glob
import datetime
from datetime import date
# from newsapi import NewsApiClient
import json
from os.path import join

#rawr
# api = open("/home/kl/github/Uwu/api.txt", "r").readline()

def update_pair(tick, history_path="history", all_day_min = False):

    path = history_path
    path = join(path,tick)

    d = glob.glob(join(history_path , "*"))

    if join(history_path,tick,"min.csv") not in d:
        
        day = get_day(tick)
        day.to_csv(join(path,"day.csv"), index=False)
        hr = get_hr(tick)
        hr.to_csv(join(path,"hr.csv"), index=False)
        min = get_min(tick, all_days=True)
        min.to_csv(join(path, "min.csv"), index=False)
        

    else:
        hr = get_day(tick)
        min = get_min(tick)
        day = get_day(tick)

        oldhr = pd.read_csv(join(path, "hr.csv"))
        oldmin = pd.read_csv(join(path ,"min.csv"))
        oldday = pd.read_csv(join(path ,"day.csv"))

        nhr = pd.concat([oldhr, hr]).drop_duplicates().sort_values(by="Datetime")
        nmin = pd.concat([oldmin, min]).drop_duplicates().sort_values(by="Datetime")
        nday = pd.concat([oldday, day]).drop_duplicates().sort_values(by="Datetime")


        nhr.to_csv(join(path ,"hr.csv"), index=False)
        nmin.to_csv(join(path ,"min.csv"), index=False)
        nday.to_csv(join(path ,"day.csv"), index=False)

        f = open(join(path, f"{tick}_update.txt"), "a")
        f.write("\n" + date.today().strftime("%m-%d-%Y"))
        f.close()
    

def update_news_h(data,path,name):
    """Complete path to the desired save location. Creates new file if none exists at location"""


    npath = join(path,"news",f"{name}.csv")
        
    if (os.path.exists(npath) == False):
        data.sort_values(by="Datetime",ascending=True).to_csv(npath, index=False)
    else:
        old_news = pd.read_csv(npath).iloc[1:,:]
        new_news = pd.concat([old_news,data]).drop_duplicates().sort_values(by="Datetime", ascending=True)
        ivd = np.zeros(len(new_news.columns))
        ivd[0] = new_news.iloc[0,0] -1
        ivd = pd.DataFrame([ivd],columns=new_news.columns)
        new_news = pd.concat([new_news,ivd]).sort_values(by="Datetime", ascending=True)
        new_news.to_csv(npath,index=False)
    

def update_news_raw(tick, path="history"):

    """Needs completed path to news folder"""

    path = join(path,tick)


    if (os.path.exists(path) == False):
        os.mkdir(path)

    n1, name1 = news1(tick) 
    update_news_h(n1,path,name1)

    n2, name2 = news2(tick)
    update_news_h(n2,path,name2)

def update_labels(pair,history_path="history"):
    """Takes in path to history"""

    npath = join(history_path,pair)

    d = glob.glob(join(npath, "news","*"))
    day = pd.DataFrame()
    hr =  pd.DataFrame()
    min = pd.DataFrame()
    
    fx_day = pd.read_csv(join(npath, "day.csv"))
    fx_hr = pd.read_csv(join(npath, "hr.csv"))
    fx_min = pd.read_csv(join(npath, "min.csv"))

    
    c = 0
    for n in d:
        t = pd.read_csv(n)
        new_news = expand_news(fx_day,t)
        for i in new_news.columns:
            day[f"{c}"] = new_news[i]
            c+=1
    
    c = 0
    for n in d:
        t = pd.read_csv(n)
        new_news = expand_news(fx_hr,t)
        for i in new_news.columns:
            hr[f"{c}"] = new_news[i]
            c+=1
    
    c = 0
    for n in d:
        t = pd.read_csv(n)
        new_news = expand_news(fx_min,t)
        for i in new_news.columns:
            min[f"{c}"] = new_news[i]
            c += 1

    day.to_csv(join(npath, "news_day.csv"), index = False)
    hr.to_csv(join(npath, "news_hr.csv"), index = False)
    min.to_csv(join(npath, "news_min.csv"), index = False)

    
    


# usd_currency_pairs = [
#     "AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY",  # Major currency pairs
#     "AUDUSD", "CADUSD", "CHFUSD", "EURUSD", "GBPUSD", "JPYUSD", "NZDUSD",  # Cross currency pairs
#     "USDCNH", "USDRUB", "USDTRY", "USDZAR", "USDSEK", "USDSGD", "USDNOK", 
#     "USDDKK", "USDCZK", "USDHKD", "USDSAR", "USDKRW", "USDTWD", "USDIDR", 
#     "USDINR", "USDPHP", "USDMYR", "USDTHB", "USDPKR", "USDVND", "USDCLP", 

#     "USDBRL", "USDCOP", "USDPEN", "USDARS", "USDVEF", "USDUYU"
# ]
