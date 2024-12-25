from datetime import date, timedelta
import matplotlib.pyplot as plt
from oandapyV20 import API
from os.path import join
import yfinance as yf
import pandas as pd
import numpy as np
import oandapyV20
import datetime
import random
import glob
import time
import json
import sys
import os



from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.endpoints.pricing import PricingStream
import oandapyV20.endpoints.instruments as instruments
from oandapyV20.endpoints.pricing import PricingInfo
import oandapyV20.endpoints.positions as Positions
import oandapyV20.endpoints.accounts as Account
import oandapyV20.endpoints.pricing as Pricing

import oandapyV20.endpoints.orders as Order
from oandapyV20.exceptions import V20Error





def calculate_ema(prices, period):
    
    ema = []
    k = 2 / (period + 1)
    ema.append(prices[0])  # Start with the first closing price as the first EMA

    for i in range(1, len(prices)):
        ema.append(prices[i] * k + ema[i-1] * (1 - k))

    return np.array(ema)

    

def log(*argv):

    # Creates file if not exist
    if not os.path.exists("log.txt"):
        a = open("log.txt", "w")
        a.close()
    
    # logs data given to function
    b = open("log.txt", "a")
    for arg in argv:
        b.write(arg)
        b.write("\n")

    b.close()

def pricelog(*argv):

    # logs data given to function
    if not os.path.exists("pricelog.txt"):
        a = open("pricelog.txt", "w")
        a.close()
    b = open("pricelog.txt", "a")
    for arg in argv:
        b.write(arg)
        b.write("\n")

    b.close()
    


def start(log_off=False):

    settings = json.load(open("settings.json"))["Settings"]
    required = ["Api Key","Account ID","Trade Duration", "Trade Interval"]
    
    # Makes sure settings are proper
    missing = []

    for i in required:
        if i not in settings:
            missing.append(i)
    if len(missing) != 0:
        print("Missing parameters in settings: \n")
        for i in missing:
            print(f"\t-{i}\n")
        
    # assert len(missing) == 0, f"Missing {missing} in settings"
    if len(missing) != 0:
        sys.exit(0)

    pairs = list(settings['Pair Settings'].keys())
    start_time = datetime.datetime.now().timestamp()
    s = f"Started at {start_time:.4f}\n"
    print(s)

    if log_off:
        return start_time, settings
    
    log(s)
    return start_time, settings


def end(start_time, log_off=False):
    endtime = datetime.datetime.now().timestamp()
    dt = f"Time elapsed {endtime-start_time}"
    endt = f"Ended at {endtime}"
    print(dt)
    print(endt)

    if log_off:
        return 
    
    log (dt)
    log(endt)

    return 


#### Descrete Methods (deriv, integral)
### Note useful for storage, integrating into main logic

# deriv - Derivative
# integ - Integral
# calculate_ema - Helper function mostly
# calculate_ema_cross(closing_arr) - Descrete to calcualte ema cross
# calculate_macd(closing_arr) - Descrete method to calcualte macd

def deriv(arr):
    """ Descrete derivative """
    
    darr = np.zeros(len(arr))

    for i in range(1,len(darr)):
        darr[i] = arr[i] - arr[i-1]
    
    if len(darr) > 2:
        darr[-1] = darr[-2] - darr[-3]

    if len(darr) <= 1:
        return np.array([0])
    
    darr[0] = darr[1]
    
    return darr

def calculate_ema(prices, period):
    ema = []
    k = 2 / (period + 1)
    ema.append(prices[0])  # Start with the first closing price as the first EMA
    for i in range(1, len(prices)):
        ema.append(prices[i] * k + ema[i-1] * (1 - k))
    return np.array(ema)

def calculate_ema_cross(closing, short_ema_period=12, long_ema_period=26):
    """
    
    Returns long, short, ema
    """
    
    ema_short = calculate_ema(closing, short_ema_period)
    ema_long = calculate_ema(closing, long_ema_period)

    ema_cross = []
    for i in range(len(ema_short)):
        if i >= long_ema_period:  # Ignore initial undefined points
            if ema_short[i] > ema_long[i]:
                ema_cross.append(1)  # 1 for bullish crossover
            elif ema_short[i] < ema_long[i]:
                ema_cross.append(-1)  # -1 for bearish crossover
            else:
                ema_cross.append(0)  # 0 for no crossover

    return ema_long, ema_short, ema_cross

def calculate_macd(closing, short_period=12, long_period=26, signal_period=9):
    ema_short = calculate_ema(closing, short_period)
    ema_long = calculate_ema(closing, long_period)
    macd_line = ema_short - ema_long
    signal_line = calculate_ema(macd_line, signal_period)
    macd_histogram = macd_line - signal_line
    return macd_line, signal_line, macd_histogram


#### Stil lworking on functions

def get_bias(l,s,c, cutoff=0,view = False,adtitle=''):
    """ cutoff cuts off the array"""
    
    # Counts the derivatives, basically a weighted scale if go up or down
    ds = cutoff
    long = l
    short = s
    cross = None
    assert cutoff < len(long), f"cutoff needs to be < {len(long)}"
    long = long[cutoff : ]
    short = short[cutoff: ]
    dlong = deriv(long)
    dshort = deriv(short)
    spos = (dshort >= 0).sum() / len(short)
    sneg = (dshort < 0).sum() / len(short)
    short_bias = (1 if spos>sneg else -1)
    lpos = (dlong >= 0).sum() / len(long)
    lneg = (dlong < 0).sum() / len(long)
    long_bias = (1 if lpos > lneg else -1)

    if view:
            fig = figure(figsize=(10,7))
            fig.add_subplot(2,2,1)
            plt.plot(short,label="Short")
            plt.plot(long,label="Long")
            plt.title(f"Regular {adtitle}")
            plt.grid(True)
            plt.legend()

            fig.add_subplot(2,2,2)
            plt.plot(dshort,label="Short")
            plt.plot(dlong,label="Long")
            plt.title(f"Derivative {adtitle}")
            plt.grid(True)
            plt.legend()

    cross_arr = np.zeros(len(long))
    for i in range(len(long)):
        if short[i] > long[i]:
            cross_arr[i] = 1
        else:
            cross_arr[i] = -1

    cpos = (cross_arr >= 0).sum()/len(cross_arr)
    cneg = (cross_arr < 0).sum()/len(cross_arr)
    cross_bias = (1 if cpos > cneg else -1)

    return  long_bias, short_bias, cross_bias
































### From old forex utils file


def get_day(pair):
    pair = pair+"=X"
    data = yf.download(pair, interval= "1d", period = "max",progress=False, ignore_tz=True).reset_index()
    data.rename(columns={"Date":"Datetime"},inplace=True)
    data["Datetime"]  = data.Datetime.apply(lambda x: x.timestamp())
    return data.iloc[:,0:6]

def get_hr(pair):
    pair = pair+"=X"
    data = yf.download(pair, interval= "1h", period = "2y",progress=False, ignore_tz=True).reset_index()

    data["Datetime"] = data.Datetime.apply(lambda x: x.timestamp())
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
    data["Datetime"] = data.Datetime.apply(lambda x: x.timestamp())
    return data.iloc[:,0:6]



def update_pair(pair, history_path="history", all_day_min = False):

    path = history_path
    path = join(path,pair)

    d = glob.glob(join(history_path , "*"))

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




        
def get_safties(arr):
    """
    :params 
        arr - 1d array of macd, whether short or long
    
    :out
        [safe_top, safe_bottom] - two floats one positiove one bottom indicating the region of saftey to buy     
    """

    carr = arr.copy()
    darr = deriv(carr)
    s = -1
    for i in range(len(darr)):
        if darr[i] < 0 and s < 0 or darr[i] > 0 and s > 0:
            s *= -1
        else:
            carr[i] = 0
    
    safe_top = 0
    c_top = 0
    
    for i in carr:
        if i > 0:
            safe_top += i
            c_top += 1

    safe_bottom = 0
    c_bottom = 0

    for i in carr:
        if i < 0:
            safe_bottom += i
            c_bottom += 1


    safe_bottom /= (c_bottom if c_bottom != 0 else 1)
    safe_top /= (c_top if c_top != 0 else 1)
    return [safe_top,safe_bottom]

def get_safties_dst(arr):
    """ Return an average when macd pivots """
    t = []
    
    carr = arr.copy()
    darr = deriv(carr)
    s = -1
    for i in range(len(darr)):
        if darr[i] < 0 and s < 0 or darr[i] > 0 and s > 0:
            s *= -1
        else:
            carr[i] = 0

    c = 0
    for i in carr:
        if i != 0:
            t.append(c)
            c = 0
        else:
            c += 1 
    
    # return np.array(t).mean()
    return t

def smooth_ma(arr_, amt=6):
    arr = arr_.copy()
    arr[0] = arr_[0]
    for j in range(amt):
        for i in range(2,len(arr)):

            mid = (arr[i] - arr[i-1])/2
            arr[i-1] += mid
            arr[i] -= mid
            
    return arr
