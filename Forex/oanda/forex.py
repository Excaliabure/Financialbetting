import matplotlib.pyplot as plt
from os.path import join
import yfinance as yf
from utils import *
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

# from newsapi import NewsApiClient

from oandapyV20.contrib.requests import MarketOrderRequest
from oandapyV20.endpoints.pricing import PricingStream
import oandapyV20.endpoints.instruments as instruments
from oandapyV20.endpoints.pricing import PricingInfo
import oandapyV20.endpoints.positions as Positions
import oandapyV20.endpoints.accounts as Account
import oandapyV20.endpoints.pricing as Pricing

import oandapyV20.endpoints.orders as Order
from oandapyV20.exceptions import V20Error
from oandapyV20 import API

# ENABLE_NEWS_SAVING = False
 
class forex():

    def __init__(self, pair = "EURUSD", path="history", mode="min", deep_update= True):
        pair = pair.replace("_","")

        self.path_pair = join(path,pair)
        self.path = path
        
        self.pair = pair
        
        self.mode = mode
    
        if (not os.path.exists(join(path))): # Creates core history
            os.mkdir(path) 

        if (self.path_pair not in glob.glob(join(path,"*"))): # Creates Pair dir
            os.mkdir(self.path_pair) 

        if (not os.path.exists(join(self.path_pair, f"{pair}_update.txt"))): # Creates update.txt
            temp = open(join(self.path_pair,f"{pair}_update.txt"), 'x')
            temp.write("0")
            temp.close()
        
        if (join(self.path_pair, "news") not in glob.glob(join(self.path_pair, "news"))): # Creates news
            os.mkdir(join(self.path_pair, "news"))

        g = open(join(self.path_pair, f"{self.pair}_update.txt"), "r+")
        temp = g.readlines()[-1]
        
        # Daily updates
        if (temp != datetime.datetime.today().strftime("%m-%d-%Y")):
            print("Note this may take a while\nUpdating...")
            update_pair(self.pair)
            # update_news_raw(self.pair, path = self.path)
            g.write("\n" + datetime.datetime.today().strftime("%m-%d-%Y"))
        g.close()



        self.hr_const = pd.read_csv(join(self.path_pair, "hr.csv"))
        self.min_const = pd.read_csv(join(self.path_pair, "min.csv"))
        self.day_const = pd.read_csv(join(self.path_pair,"day.csv"))
        self.hr = pd.read_csv(join(self.path_pair, "hr.csv"))
        self.min = pd.read_csv(join(self.path_pair, "min.csv"))
        self.day = pd.read_csv(join(self.path_pair, "day.csv"))


    def update(self,force_news = False):
        update_pair(self.pair)

        # if force_news:
            # update_news_raw(self.pair) 
            # update_labels(self.pair)


    def add_senti(self,force_update=False):
      # Adds sentiment column 

        # Just checks if the days need updating based on len
        aday = pd.read_csv(join(self.path_pair, "news_day.csv"))
        cday = pd.read_csv(join(self.path_pair ,"day.csv"))

        # if (len(aday) != len(cday) or force_update):
            # update_labels(self.pair)

        self.day = self.day_const
        self.hr  = self.hr_const
        self.min = self.min_const

        aday = pd.read_csv(join(self.path_pair, "news_day.csv"))
        ahr = pd.read_csv(join(self.path_pair,"news_hr.csv"))
        amin = pd.read_csv(join(self.path_pair,"news_min.csv"))
        
        self.day = pd.concat([self.day,aday],axis=1)
        self.hr = pd.concat([self.hr,ahr],axis=1)
        self.min = pd.concat([self.min,amin],axis=1)

   
       
    def as_yf(self, x):
        d = x.copy()
        d["Datetime"] = d["Datetime"].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S"))#.set_index("Datetime")
        d.set_index("Datetime",inplace=True)
        d["Volume"] = [0 for i in range(len(d))]
        
        return d
    
    
    def all_get_pairs(self, arr):

            
        for i in arr:
            if not os.path.exists(join(self.path,i)):
                os.mkdir(join(self.path,i))

        for i in arr:
            try:
                update_pair(i)
            except:
                print(f"Not Found: {i}")
        

    def all_day(self):

        path = self.path
        files = glob.glob(join(path, "*"))

        lb = min([len(pd.read_csv(join(f, "day.csv"))) for f in files ])
        t = pd.DataFrame()

        for i in files:
            _c = pd.read_csv(join(i, "day.csv"))["Close"][:lb-1].rename(i.removeprefix("history").replace("\\",""))
            t = pd.concat([t,_c],axis=1)

        return t



class ForexApi():
    def __init__(self,pair_c="EUR_USD"):
        """ Describe """

        if not os.path.exists("settings.json"):
            a = open("settings.json","w")
            a.write("{\n\n}")
            a.close()

        s = json.load(open("settings.json"))["Settings"]
        apikey = s["Api Key"]
        self.accountid = s["Account ID"]
        self.api = API(access_token=apikey, environment="practice", headers={"Accept-Datetime-Format": "UNIX"})
        self.pair = pair_c
        self.history = forex(pair_c.replace("_",""))
        self.current_focus = "hr"
        self.arr = self.history.hr.to_numpy()

        if not os.path.exists("log.txt"):
            a = open("log.txt","w")
            a.close()


    def change_focus(self,f="hr"):
        self.current_focus = f
        if f == "min":
            self.arr = self.history.min.to_numpy()
        elif f == "day":
            self.arr = self.history.day.to_numpy()
        else:
            self.arr = self.history.hr.to_numpy()
        return f

    def buy_sell(self, pair, units, pip_diff, view=False, terminal_print=True, time_In_Force="FOK",type_="MARKET", price="1"):
        """ 
        :params
            pair - forex pair, ex [EURUSD EUR/USD EUR_USD] are all valid formats
            units - How much to buy. - value makes sell postiion and + makes but position
            view - Doesnt execute the order, just displays the order to fill
        If position is negative, sell pos, else pos buy pos"""

        
        p = (str(units) if type(units) == str else units)
        pip = 1e-4
        p = pair

        if "_" not in p:
            p = pair[:3] + "_" + pair[3:]

        request = PricingInfo(accountID=self.accountid, params={"instruments": p})
        response = self.api.request(request)

        # Extract bid and ask prices from the response
        prices = response.get("prices", [])
        asset_price = float(prices[0]['asks'][0]['price'])
        basediff = pip * pip_diff
        tp = asset_price + (-basediff if units  < 0 else basediff)
        sl = asset_price - (-basediff if units  < 0 else basediff)

        order_info = {
            "order": {
                "price": price,
                "takeProfitOnFill": {
                        "timeInForce": "GTC",
                        "price": str(round(tp,5))
                    },
                "stopLossOnFill": {
                    "timeInForce": "GTC",
                    "price": str(round(sl,5))
                    },
                
            "timeInForce": "FOK",
            "instrument": p,
            "units": str(units),
            "type": type_,
            "positionFill": "DEFAULT"
            }
        }
        

        if terminal_print:
            print(order_info)
        
        if view:
            return order_info
        else:
            o = Order.OrderCreate(self.accountid,order_info)
            resp = self.api.request(o)
            
            return resp
    

    def get_pair(self, _pair, count=1, granularity="M1", return_price_1=True):
        
        p = _pair
        if "_" not in p:
            p = _pair[:3] + "_" + _pair[3:]

        f = json.load(open("settings.json"))["Settings"]

        current_time = datetime.datetime.now()
        start_time = (current_time - datetime.timedelta(minutes=50)).isoformat() + "Z"
        end_time = current_time.isoformat() + "Z"

        parm = {
            "instruments" : p,
            "granularity": granularity,
            "from": start_time,
            "to": end_time
        }


        request = PricingInfo(accountID=self.accountid, params=parm)
        response = self.api.request(request)

        # Extract bid and ask prices from the response
        prices = response.get("prices", [])
        asset_price = float(prices[0]['asks'][0]['price'])

        return response

        
    def close(self, _pair):
        """ Closes specific order"""
        

        pair = (_pair if "_" in _pair else _pair[:3] + "_" + _pair[3:])
        list_orders = Positions.OpenPositions(self.accountid)
        order_dict = self.api.request(list_orders)
        plist = order_dict['positions']
        pair_info = None

        for i in plist:
            if i['instrument'] == pair:       
                pair_info = plist[0]
            else:
                pair_info = None    

        if pair_info == None:
            return -1
        else:
            toclose = ({"longUnits" : "ALL"} if int(pair_info['long']['units']) != 0 else {"shortUnits" : "ALL"})
        
        try:
            req = Positions.PositionClose(accountID=self.accountid, instrument=pair, data=toclose)
            self.api.request(req)
            # return float(pair_info['unrealizedPL'])
            return 1
        except:
            # print(f"UNABLE TO CLOSE {pair} (DNE)")
            return 0

    def close_all(self):
        """ Closes all orders"""
        list_orders = Positions.OpenPositions(self.accountid)
        order_dict = self.api.request(list_orders)
        plist = order_dict['positions']
        cpl = 0
        
        for i in plist:
            toclose = ({"longUnits" : "ALL"} if int(i['long']['units']) != 0 else {"shortUnits" : "ALL"})
        
            req = Positions.PositionClose(accountID=self.accountid, instrument=i['instrument'], data=toclose)
            self.api.request(req)
            time.sleep(0.1)
        for i in order_dict['positions']:
            cpl += float(i['unrealizedPL'])    
        
        return cpl
    

    def view(self,_pair=None,gen_info=False):
        """ Views info of pair """

        list_orders = Positions.OpenPositions(self.accountid)
        account_info = Account.AccountDetails(self.accountid)
        positions = self.api.request(list_orders)
        acc_info = self.api.request(account_info)
        
        if gen_info:
            return acc_info

        if _pair == None:
            return positions

        else:
            pair = (_pair if "_" in _pair else _pair[:3] + "_" + _pair[3:]) 

            for i in positions['positions']:
                if i['instrument'] == pair:
                    return i
        # Return None if not found
        return None
    
    

    def get_ema_cross(self, _pair="Current", timeframe="M1",long_ema_period=26,short_ema_period=9):
        """
        :params
            pair - pair in the format of "xxx_xxx"
            timeframe - M5 = Minute 5, H1 = Hour 1, and so on
            long_ema_period - idk lol. Dictates the length of the ema 
            short_ema_period - idk 
        
        :out
            long ema
            short ema
            cross 

        """
        pair = self.pair
        
        # Construct the EMA requests
        short_ema_params = {
            'granularity': timeframe,
            'count': long_ema_period +1,  # Include extra data points for EMA calculation
        }
        long_ema_params = {
            'granularity': timeframe,
            'count': long_ema_period + 1,  # Include extra data points for EMA calculation
        }
        
        if _pair != "Current":
            pair = _pair
        
        short_req = instruments.InstrumentsCandles(instrument=pair,
                                                    params=short_ema_params)
        long_req = instruments.InstrumentsCandles(instrument=pair,
                                                    params=long_ema_params)
        
        # Make the requests to fetch historical data for both EMAs  
        short_ema_response = self.api.request(short_req)
        long_ema_response = self.api.request(long_req)

        # return short_ema_response, long_ema_response, None
        # Extract the closing prices from the responses
        short_prices = [float(candle['mid']['c']) for candle in short_ema_response['candles']]
        long_prices = [float(candle['mid']['c']) for candle in long_ema_response['candles']]
        
        # Calculate EMAs using exponential smoothing
        def c_ema(prices, period):
            ema = []
            multiplier = 2 / (period + 1)
            ema.append(prices[0])  # Initial EMA is the first price
            for i in range(1, len(prices)):
                ema.append((prices[i] - ema[-1]) * multiplier + ema[-1])  # EMA formula
            return ema

        short_ema_values = c_ema(short_prices, short_ema_period)
        long_ema_values = c_ema(long_prices, long_ema_period)

        # Calculate EMA crossover
        ema_cross = []
        for i in range(len(short_ema_values)):
            if i >= long_ema_period:  # Ignore initial undefined points
                if short_ema_values[i] > long_ema_values[i]:
                    ema_cross.append(1)  # 1 for bullish crossover
                elif short_ema_values[i] < long_ema_values[i]:
                    ema_cross.append(-1)  # -1 for bearish crossover
                else:
                    ema_cross.append(0)  # 0 for no crossover

        return np.array(long_ema_values), np.array(short_ema_values), np.array(ema_cross)
    

    def get_macd(self, _pair="Current", timeframe="M1", short_ema_period=9, long_ema_period=26, signal_period=9, truncated=True):
        """
        :params
            pair - pair in the format of "xxx_xxx"
            timeframe - M5 = Minute 5, H1 = Hour 1, and so on
            short_ema_period - Short EMA period (default 12)
            long_ema_period - Long EMA period (default 26)
            signal_period - Signal line EMA period (default 9)
            truncated - Makes mline,sline,histo have a length of 27

        :out
            macd line
            signal line
            histogram
        """
        
        # Fetch historical data
        ema_params = {
            'granularity': timeframe,
            'count': long_ema_period + signal_period + 1,  # Include extra data points for EMA calculation
        }

        pair = self.pair
        if _pair != "Current":
            pair = _pair
        
        req = instruments.InstrumentsCandles(instrument=pair, params=ema_params)
        response = self.api.request(req)

        # Extract the closing prices from the response
        prices = [float(candle['mid']['c']) for candle in response['candles']]
        
        # Calculate EMAs using exponential smoothing
        def calculate_ema(prices, period):
            ema = []
            multiplier = 2 / (period + 1)
            ema.append(prices[0])  # Initial EMA is the first price
            for i in range(1, len(prices)):
                ema.append((prices[i] - ema[-1]) * multiplier + ema[-1])  # EMA formula
            return ema

        short_ema_values = calculate_ema(prices, short_ema_period)
        long_ema_values = calculate_ema(prices, long_ema_period)

        # Calculate MACD line (difference between short EMA and long EMA)
        macd_line = [short_ema_values[i] - long_ema_values[i] for i in range(len(short_ema_values))]

        # Calculate Signal line (EMA of MACD line)
        signal_line = calculate_ema(macd_line, signal_period)

        # Calculate MACD histogram (difference between MACD line and Signal line)
        macd_histogram = [macd_line[i] - signal_line[i] for i in range(len(signal_line))]
        macd_line = np.array(macd_line)
        signal_line = np.array(signal_line)
        macd_histogram = np.array(macd_histogram)

        if truncated:
            return macd_line[9:], signal_line[9:], macd_histogram[9:]
        else:
            return macd_line, signal_line, macd_histogram
    
    
    def deriv(self):
        """ Descrete derivative """

        _deriv = lambda arr: [arr[i] - arr[i-1] for i in range(1,len(arr))] 
        
        if len(self.history.hr) <= 1 or len(self.history.day) <= 1 or len(self.history.min) <= 1:
            print(" Error with History ")
            return
        
        return _deriv(self.focus[:,4])
    
    def integral(self):
        """ Idk dont need rn, gonna keep it trapizoid method"""
        arr = self.focus
        temp = np.array([(arr[k-1] + arr[k]) for k in range(1,len(arr))]) / 2
        return temp










    def get_pl(self):

        list_orders = Positions.OpenPositions(self.accountid)
        response = self.api.request(list_orders)
        
        price_losses = {}

        for i in response['positions']:
            price_losses[i['instrument']] = float(i['unrealizedPL'])


        return price_losses
    
    def get_info(self):

        bal = Account.AccountDetails(self.accountid)
        response = self.api.request(bal)
        return response['account']
    














    def update_history(self):

        forex(self.pair).update()
        return 












    def log_info(self,log_off=False):
        if log_off:
            return

        if not os.path.exists("pricelog.csv"):
            f = open("pricelog.csv", "w")
            f.write("Time,Bal,Pl\n")
            f.close()
        bal = Account.AccountDetails(self.accountid)
        response = self.api.request(bal)
        a = response['account']
        # logs data given to function

        f = open("pricelog.csv", "a")

        bal =  float(a['balance'])
        pl = float(a['pl'])
        t = datetime.datetime.now().timestamp()#.strftime("%H:%M:%S")

        f.write(f"{t},{bal},{pl}\n")
        f.close()
        return 
    