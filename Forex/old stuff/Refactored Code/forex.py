import torch
import torch.nn as nn
import yfinance as yf
import pandas as pd
# from newsapi import NewsApiClient
from utils import *
from update import *
import pandas
from datetime import datetime
from os.path import join
from news_utils import *



class forex():

    def __init__(self, pair, history_path="history", mode="min", dtype=None, quiet=True):

        self.pair_path = join(history_path,pair)
        self.pair = pair
        self.mode = mode
    
        # try:
        #     g = open(join(self.pair_path, f"{self.pair}_update.txt"), "r").readlines()[-1].split("/")
        #     if (quiet == True):
        #         pass
        #     else:
        #         print(f"Most recent update for {self.pair}: {g[0]}")
            
        #     if (g[0] != datetime.datetime.today().strftime("%m-%d-%Y")):
        #         print("Note this may take a while")
        #         print("Updating...")
                

        #         update_pair(self.pair, path = self.path)
        #         # Only update_pair is allowed to be called first
        #         # Any other updates call below update pair
        #         update_news_raw(self.pair, path = self.path)
                
        # except:
        #     print("Update file not found \nCreating necessary files...")
        #     update_pair(self.pair, path = self.path)

        #     print("Note this may take a while")
        #     print(f"Updating News at {self.path}")
        #     update_news_raw(self.pair, history_path = self.path)


        # self.hr_const = pd.read_csv(join(self.path, "hr.csv"))
        # self.min_const = pd.read_csv(join(self.path , "min.csv"))
        # self.day_const = pd.read_csv(join(self.path,"day.csv"))




        # self.hr = pd.read_csv(join(self.path, "hr.csv"))
        # self.min = pd.read_csv(join(self.path, "min.csv"))
        # self.day = pd.read_csv(join(self.path, "day.csv"))

        

        
    # def update(self, news=False):
    #     print("Note this may take a while")
    #     print(f"Updating database at {self.path}")
        
    #     update_pair(self.pair, history_path=self.path)
    #     if news:
    #         update_news_raw(self.pair)
    #         update_labels(self.pair)

    #     print("Updated")

    # def get_all_pairs(self):

    #     """ Note this function is only meant to be used once to fetch all pairs """

    #     usd_pairs = [
    #         'EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD', 'USDJPY', 'USDCHF', 'USDCAD',
    #         'USDSGD', 'USDHKD', 'USDSEK', 'USDNOK', 'USDTRY', 'USDMXN', 'USDZAR',
    #         'USDINR', 'USDBRL', 'USDRUB', 'USDTHB', 'USDKRW', 'USDCNY', 'USDTWD',
    #         'USDPHP', 'USDIDR', 'USDMYR', 'USDARS', 'USDCOP', 'USDCLP', 'USDVND',
    #         'USDDKK', 'USDPLN', 'USDCZK', 'USDHUF', 'USDILS', 'USDQAR', 'USDSAR',
    #         'USDNGN', 'USDEGP', 'USDKWD', 'USDPKR', 'USDLKR', 'USDBDT', 'USDMMK',
    #         'USDKES', 'USDUAH', 'USDCRC', 'USDPEN', 'USDCLP', 'USDUYU', 'USDPYG'
    #         # Add more pairs as needed
    #     ]

    #     forex_pairs = [
    #     'EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 'AUDUSD', 'USDCAD', 'NZDUSD',
    #     'EURGBP', 'EURJPY', 'GBPJPY', 'CHFJPY', 'AUDJPY', 'CADJPY', 'NZDJPY',
    #     'GBPCHF', 'EURCHF', 'AUDCHF', 'CADCHF', 'NZDCHF', 'EURAUD', 'GBPAUD',
    #     'AUDCAD', 'NZDCAD', 'EURCAD', 'GBPCAD', 'GBPNZD', 'EURNZD', 'AUDNZD',
    #     'CADNZD', 'USDSGD', 'EURSGD', 'GBPSGD', 'AUDSGD', 'NZDSGD', 'USDHKD',
    #     'EURHKD', 'GBPHKD', 'AUDHKD', 'NZDHKD', 'USDZAR', 'EURZAR', 'GBPZAR',
    #     'AUDZAR', 'NZDZAR', 'USDMXN', 'EURMXN', 'GBPMXN', 'AUDMXN', 'NZDMXN',
    #     'USDSEK', 'EURSEK', 'GBPSEK', 'AUDSEK', 'NZDSEK', 'USDNOK', 'EURNOK',
    #     'GBPNOK', 'AUDNOK', 'NZDNOK', 'USDDKK', 'EURDKK', 'GBPDKK', 'AUDDKK',
    #     'NZDDKK', 'USDPLN', 'EURPLN', 'GBPPLN', 'AUDPLN', 'NZDPLN', 'USDHUF',
    #     'EURHUF', 'GBPHUF', 'AUDHUF', 'NZDHUF', 'USDCZK', 'EURCZK', 'GBPCZK',
    #     'AUDCZK', 'NZDCZK', 'USDTRY', 'EURTRY', 'GBPTRY', 'AUDTRY', 'NZDTRY',
    #     'USDBRL', 'EURBRL', 'GBPBRL', 'AUDBRL', 'NZDBRL',
    # ]

    #     fetch_em = []

    #     p =  glob.glob(join(self.path, "*"))
    #     for i in range(len(p)):
    #         p[i] = p[i].split("/")[-1].split(".")[0]
    #     for i in usd_pairs:
    #         if i not in p:
    #             fetch_em.append(i)
    #     if len(fetch_em) == 0:
    #         print("All pairs fetched")
           
    #     else:
    #         print(f"Fetching {len(fetch_em)} pairs...")
    #         for i in fetch_em:
    #             update_pair(i, path=self.path)
    #         print("All pairs fetched")
           

    # def info(self):

    #     print(f"Pair: {self.pair}")
    #     print(f"Path: {self.path}")
    #     print(f"Mode: {self.mode}")


    # # All the function below are meant to add data to all of them

    # def add_senti(self,force_update=False):
    #     # Adds sentiment column 


    #     aday = pd.read_csv(join(self.path, "news_day.csv"))
    #     cday = pd.read_csv(join(self.path ,"day.csv"))


    #     if (len(aday) != len(cday) or force_update):
    #         update_labels(self.pair)

    #     self.day = self.day_const
    #     self.hr  = self.hr_const
    #     self.min = self.min_const


    #     aday = pd.read_csv(join(self.path, "news_day.csv"))
    #     ahr = pd.read_csv(join(self.path,"news_hr.csv"))
    #     amin = pd.read_csv(join(self.path,"news_min.csv"))
        
    #     self.day = pd.concat([self.day,aday],axis=1)
    #     self.hr = pd.concat([self.hr,ahr],axis=1)
    #     self.min = pd.concat([self.min,amin],axis=1)
        
       
    # def as_yf(self, x):
    #     d = x.copy()
    #     d["Datetime"] = d["Datetime"].apply(lambda x: datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S"))#.set_index("Datetime")
    #     d.set_index("Datetime",inplace=True)
    #     d["Volume"] = [0 for i in range(len(d))]
    #     return d
    
    
    
