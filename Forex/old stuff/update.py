import yfinance as yf
import pandas as pd
import numpy as np
from utils import *
from news_utils import * 
import os
from glob import glob
import datetime
from datetime import date
# from newsapi import NewsApiClient
import json
from os.path import join

#rawr
# api = open("/home/kl/github/Uwu/api.txt", "r").readline()

def update_pair(pair, history_path="history", all_day_min = False):

    path = history_path
    path = join(path,pair)

    d = glob(join(history_path , "*"))

    if join(history_path,pair,"min.csv") not in d:
        
        day = get_day(pair)
        day.to_csv(join(path,"day.csv"), index=False)
        hr = get_hr(pair)
        hr.to_csv(join(path,"hr.csv"), index=False)
        min = get_min(pair, all_days=True)
        min.to_csv(join(path, "min.csv"), index=False)
        

    else:
        hr = get_day(pair)
        min = get_min(pair)
        day = get_day(pair)

        oldhr = pd.read_csv(join(path, "hr.csv"))
        oldmin = pd.read_csv(join(path ,"min.csv"))
        oldday = pd.read_csv(join(path ,"day.csv"))

        nhr = pd.concat([oldhr, hr]).drop_duplicates().sort_values(by="Datetime")
        nmin = pd.concat([oldmin, min]).drop_duplicates().sort_values(by="Datetime")
        nday = pd.concat([oldday, day]).drop_duplicates().sort_values(by="Datetime")


        nhr.to_csv(join(path ,"hr.csv"), index=False)
        nmin.to_csv(join(path ,"min.csv"), index=False)
        nday.to_csv(join(path ,"day.csv"), index=False)

        f = open(join(path, f"{pair}_update.txt"), "a")
        f.write("\n" + date.today().strftime("%m-%d-%Y"))
        f.close()
    


# usd_currency_pairs = [
#     "AUDUSD", "EURUSD", "GBPUSD", "NZDUSD", "USDCAD", "USDCHF", "USDJPY",  # Major currency pairs
#     "AUDUSD", "CADUSD", "CHFUSD", "EURUSD", "GBPUSD", "JPYUSD", "NZDUSD",  # Cross currency pairs
#     "USDCNH", "USDRUB", "USDTRY", "USDZAR", "USDSEK", "USDSGD", "USDNOK", 
#     "USDDKK", "USDCZK", "USDHKD", "USDSAR", "USDKRW", "USDTWD", "USDIDR", 
#     "USDINR", "USDPHP", "USDMYR", "USDTHB", "USDPKR", "USDVND", "USDCLP", 

#     "USDBRL", "USDCOP", "USDPEN", "USDARS", "USDVEF", "USDUYU"
# ]
