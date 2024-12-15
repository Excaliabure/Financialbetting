import yfinance as yf
import pandas as pd
import numpy as np
from utils import *
import os
import glob
import datetime
from datetime import date
# from newsapi import NewsApiClient
import json
import time 
import random

# Note, does not use PATH


"""
To write a function to grab news, write the function in this format

def func(pair):

    data getting 

    return pd.DataFrame([Datetime,Text, (label1, label2, ...)])


Upon completion of a function, go to update and add the two lines of code for the update_news_raw()



"""


def senti_assign(v : dict):
    val = v['score']
    if (v['label'] == 'negative'):
        val *= -1
    elif (v['label'] == 'neutral'):
        val *= 0
    else:
        val = abs(val)

    return val


def news0(tick):
    """
    Not called anywhere
    Example of creating a news grabbing function



    """


    url = f"https://www.tradingview.com/symbols/{tick}/history-timeline/"
    

    # -------------------------
    senti = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
    a = requests.get(url)
    assert a.status_code == 200, "Status code error, Maybe website is down?"
    raw_data = BeautifulSoup(a.content, 'html.parser')
    mon = {'Jan': 1,'Feb': 2,'Mar': 3,
                    'Apr': 4, 'May': 5, 'Jun': 6, 
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 
                    'Oct': 10, 'Nov': 11,'Dec': 12}
    # -------------------------------------

    # Prepared all data
    dates = None
    raw_text = None
    labels = None

    """
    Figure out how to grab data    
    """

    # Input all data
    # Note <LABELS> is refering to all the labels, not just 1 
    news = pd.DataFrame([dates,raw_text,labels], columns=["Datetime", "Text", "<LABELS>"]).sort_values("Datetime",ascending=True)
    
    # Name of webiste/api
    name = "tradeview"
    if len(news) <= 1:
        print(f"Could not find news pair for {name}")
        return news, name

    return news, name


def news1(tick):

    """
    :params
        pair - in the format of "XXXYYY" where X and Y represent currency


    :out
        news - pandas dataframe, unless as_arr = True then as an array
        -> Datetime (integer), Text (raw text), label1, label2, ...., labeln
        name - the name of the link/data
    
    
    """

    url = f"https://www.tradingview.com/symbols/{tick}/history-timeline/"
  
    # ------------------------------------
    #   uniform, just change url

    
    senti = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
    a = requests.get(url)
    assert a.status_code == 200, "Status code error, Maybe website is down?"
    b = BeautifulSoup(a.content, 'html.parser')

    mon = {'Jan': 1,'Feb': 2,'Mar': 3,
                    'Apr': 4, 'May': 5, 'Jun': 6, 
                    'Jul': 7, 'Aug': 8, 'Sep': 9, 
                    'Oct': 10, 'Nov': 11,'Dec': 12}
    # -------------------------------------

    # Prepared all data
    info = b.find_all('div', class_= "content-Pktag1eE")
    dates = b.find_all('div' , class_="date-Pktag1eE")
    
    arr_info = [q.getText() for q in info]
    arr_dates = [q.getText() for q in dates]
    arr_dates = [i[:6] + " " + i[6:] for i in arr_dates]
    
    
    for i in range(0,len(arr_dates)):
        s = arr_dates[i].split(" ")
        
        fs = f"{mon[s[0]]} {s[1]} {s[2][2:]}"
        arr_dates[i] = int(datetime.datetime.strptime(fs , '%m %d %y').timestamp())

    # arr_label = [ (-1 if senti(i)[0]['label'] == 'negative' else 1) * senti(i)[0]['score'] for i in arr_info]   
    arr_label = []
    for i in arr_info:
        senti_val = senti(i)
        arr_label.append(senti_assign(senti_val[0]))
        

    date_info = [[arr_dates[i], arr_info[i], arr_label[i]] for i in range(0,len(arr_label))]
  

    news = pd.DataFrame(date_info, columns=["Datetime", "Text", "Label"]).sort_values("Datetime",ascending=True)
    



    name = "tradeview"
    if len(news) <= 1:
        print(f"Could not find news pair for {name}")
        return news, name

    return news, name

def news2(tick):

    return None