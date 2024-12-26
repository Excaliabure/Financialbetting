import datetime 
import random
import time
from utils import log, smooth_ma
import json
import os
import numpy as np
import sys

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


######
# Modify the values 
APIKEY = None
ACCOUNTID = "101-001-27337634-002"



######

if APIKEY != None:
    ap = APIKEY
else:
    ap = input("Consider Edititng the file\nInput Api Key: ")
# ai = input("Account ID: ")
if ACCOUNTID != None:
    ai = ACCOUNTID
else:
    ai = input("Consider Editing the file\nInput Account id: ")

SETTINGS = {
    "Settings": {
        "Api Key": ap,
        "Account ID": ai,
        "Practice Account": True,
        "Trade Duration": 28800,
        "Trade Interval": 30,
        "Iterations" : 200000,
        "coef" : 0.5,
        "General Settings" : "true",
        "units" : 1000,
        "sltp" : 30,
        "count" : 7,
        "tolerance": 0.0001, 


        "Pair Settings": {
        
        "AUD_CAD": {
                "units": 1000,
                "sltp": 1000,
                "count": 2
            }
        
        }        
    }
}



class ForexApi():
    def __init__(self,pair_c="EUR_USD",settings=None):
        """ Describe """

        if not os.path.exists("settings.json"):
            a = open("settings.json","w")
            a.write("{\n\n}")
            a.close()

        if settings != None:
            s = settings["Settings"]
        else:
            s = json.load(open("settings.json"))["Settings"]
        
        apikey = s["Api Key"]
        self.accountid = s["Account ID"]
        self.api = API(access_token=apikey, environment="practice", headers={"Accept-Datetime-Format": "UNIX"})
        self.pair = pair_c
        self.current_focus = "hr"
        # self.arr = self.history.hr.to_numpy()


        if not os.path.exists("log.txt"):
            a = open("log.txt","w")
            a.close()

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
            return 1
        except:
            return 0
        
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


def smooth_ma(arr_, amt=6):
    """ Smooths out hte curve for better derivatives
    Not perfect, but get good enough smoothing"""
    arr = arr_.copy()
    arr[0] = arr_[0]
    for j in range(amt):
        for i in range(2,len(arr)):
            mid = (arr[i] - arr[i-1])/2
            arr[i-1] += mid
            arr[i] -= mid
    return arr


def algo_deriv(env,settings,start_time, ret_derivs=False):

    history_arr_dict = {}
    for pair in settings['Pair Settings'].keys():

        history_arr = np.array([])
        print("Building Derivatives...")
        for i in range(4):
            val = float(env.get_pair(pair)['prices'][0]['bids'][0]['price'])
            history_arr = np.append(history_arr, val)
            time.sleep(5.1)

        y = np.array(history_arr)
        iters = settings['Iterations']
        c = 0
        y = smooth_ma(y[len(y) - 30 : ], 3)
        ddy = deriv(deriv(y))

            
            
        cpos = -1 if ddy[-1] < 0 else 1
        pos = cpos

        env.close(pair)
        env.buy_sell(pair, 1000 * pos, 999, terminal_print = False)

        history_arr = history_arr.tolist()
        history_arr_dict[pair] = {}
        history_arr_dict[pair]["history_arr"] = history_arr
        history_arr_dict[pair]["hold_position"] = cpos
        history_arr_dict[pair]["current_position"] = pos
        history_arr_dict[pair]["hold_times"] = 2
    
        print(f"Put a {'Sell' if pos == -1 else 'Buy'} position on {pair}")


    
        time.sleep(0.5)



    while c < iters:

        for pair in settings['Pair Settings'].keys():

            pos = history_arr_dict[pair]["current_position"]
            cpos = history_arr_dict[pair]["hold_position"]
            sltp = settings['Pair Settings'][pair]["sltp"]
            tol = settings['tolerance']


            val = float(env.get_pair(pair)['prices'][0]['bids'][0]['price'])
            
            history_arr = np.array(history_arr_dict[pair]["history_arr"])
            history_arr = np.append(history_arr, val)
            y = smooth_ma(history_arr, 3)
            history_arr_dict[pair]["history_arr"] = history_arr.tolist()


            y = y[2:]
            dy = deriv(y)
            ddy = deriv(dy)
            # return y,dy,ddy



            # if abs(ddy[-1]) < 1e-5 and abs(dy[-1]) < 1e-5:
            if abs(ddy[-1] - dy[-1]) < 1e-5:
                if (dy[-2] < 0):
                    # if previous deriv is neg, gonan go down
                    cpos = 1
                else:
                    cpos = -1


            if ret_derivs:
                return y,dy,ddy
            
            if cpos != pos:
                
                q = env.close(pair)
                print(f"{pair} closed {q}")
                
                pos = cpos
                env.buy_sell(pair, 1000 * cpos, sltp, terminal_print=False)
                
                time.sleep(0.5)
                
                print()
                print(f"{'[SELL]' if cpos == -1 else '[BUY]'} position on {pair} with deriv = {ddy[-1]}")
                print()
                time.sleep(0.5)




            history_arr_dict[pair]["current_position"] = cpos
            history_arr_dict[pair]["hold_position"] = cpos
            if (env.view(pair) == None):
                print()
                print(f"No sell/buy position for {pair}. Attempting...")
                tempcurr = history_arr_dict[pair]["current_position"]
                env.buy_sell(pair, 1000 * tempcurr, sltp, terminal_print=False)
                print(f"{'[SELL]' if cpos == -1 else '[BUY]'} position on {pair} with deriv = {ddy[-1]}")
                print()

            print(f"y : {y[-1]} | dy : {dy[-2]} | ddy {ddy[-1]}")

                
            c += 1
        
        time.sleep(settings["Trade Interval"])

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
    if len(missing) != 0:
        sys.exit(0)
    start_time = datetime.datetime.now().timestamp()
    s = f"Started at {start_time:.4f}\n"
    print(s)
    
    return start_time, settings



if __name__ == '__main__':


    env = ForexApi("AUD_USD", settings=SETTINGS)
    env.log_info(log_off=True)
    start_time, settings = start(log_off=True)
    print("\n")

    algo_deriv(env,settings,start_time)
    