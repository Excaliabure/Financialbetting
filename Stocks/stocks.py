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
from news_grabber import *


class stocks():

    def __init__(self, tick, path="history", mode="min"):
        

        self.path_tick = join(path,tick)
        self.tick = tick
        self.mode = mode
    
        if (not os.path.exists(join(path))): # Creates core history
            os.mkdir(path) 

        if (self.path_tick not in glob.glob(join(path,"*"))): # Creates Pair dir
            os.mkdir(self.path_tick) 

        if (not os.path.exists(join(self.path_tick, f"{tick}_update.txt"))): # Creates update.txt
            temp = open(join(self.path_tick,f"{tick}_update.txt"), 'x')
            temp.write("0")
            temp.close()
        
        if (join(self.path_tick, "news") not in glob.glob(join(self.path_tick, "news"))): # Creates news
            os.mkdir(join(self.path_tick, "news"))

        g = open(join(self.path_tick, f"{self.tick}_update.txt"), "r+")
        temp = g.readlines()[-1]
        
        # Daily updates
        if (temp != datetime.datetime.today().strftime("%m-%d-%Y")):
            print("Note this may take a while")
            print("Updating...")
            update_pair(self.tick)
            # update_news_raw(self.pair, path = self.path)
            g.write("\n" + datetime.datetime.today().strftime("%m-%d-%Y"))
        g.close()



        self.hr_const = pd.read_csv(join(self.path_tick, "hr.csv"))
        self.min_const = pd.read_csv(join(self.path_tick, "min.csv"))
        self.day_const = pd.read_csv(join(self.path_tick,"day.csv"))

        self.hr = pd.read_csv(join(self.path_tick, "hr.csv"))
        self.min = pd.read_csv(join(self.path_tick, "min.csv"))
        self.day = pd.read_csv(join(self.path_tick, "day.csv"))

    def update(self,force_news = False):
        update_pair(self.tick)
        if force_news:
            update_news_raw(self.tick) 
            update_labels(self.tick)

    def add_senti(self,force_update=False):
      # Adds sentiment column 

        # Just checks if the days need updating based on len
        aday = pd.read_csv(join(self.path_tick, "news_day.csv"))
        cday = pd.read_csv(join(self.path_tick ,"day.csv"))


        if (len(aday) != len(cday) or force_update):
            update_labels(self.tick)

        self.day = self.day_const
        self.hr  = self.hr_const
        self.min = self.min_const


        aday = pd.read_csv(join(self.path_tick, "news_day.csv"))
        ahr = pd.read_csv(join(self.path_tick,"news_hr.csv"))
        amin = pd.read_csv(join(self.path_tick,"news_min.csv"))
        
        self.day = pd.concat([self.day,aday],axis=1)
        self.hr = pd.concat([self.hr,ahr],axis=1)
        self.min = pd.concat([self.min,amin],axis=1)

   
       
    def as_yf(self, x):
        d = x.copy()
        d["Datetime"] = d["Datetime"].apply(lambda x: datetime.fromtimestamp(x).strftime("%Y-%m-%d %H:%M:%S"))#.set_index("Datetime")
        d.set_index("Datetime",inplace=True)
        d["Volume"] = [0 for i in range(len(d))]
        return d
    
    
