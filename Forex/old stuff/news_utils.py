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


def news0(pair):
    """
    Not called anywhere
    Example of creating a news grabbing function



    """


    url = f"https://www.tradingview.com/symbols/{pair}/history-timeline/"
    

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


def news1(pair):

    """
    :params
        pair - in the format of "XXXYYY" where X and Y represent currency


    :out
        news - pandas dataframe, unless as_arr = True then as an array
        -> Datetime (integer), Text (raw text), label1, label2, ...., labeln
        name - the name of the link/data
    
    
    """

    url = f"https://www.tradingview.com/symbols/{pair}/history-timeline/"
  
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


def news2(pair):

    """
    Looks at the dailyFx news section and returns sentiment values for all the 
    given links on the page in pandas format

    
    :params
        pair - the type of pair wanted. Only tested working is EURUSD
    
    :out
        news - The pandas Dataframe, where 
        -> Datetime, Raw text, ... sn where s0-sn are sentiment values
        in this case its Header Sentiment, First 20% of doc sentiment, and last 80%
        name

    
    
    """


    url = f"https://www.dailyfx.com/{pair[:3].lower()}-{pair[3:].lower()}/news-and-analysis"
    mon = {'Jan': 1,'Feb': 2,'Mar': 3,
                'Apr': 4, 'May': 5, 'Jun': 6, 
                'Jul': 7, 'Aug': 8, 'Sep': 9, 
                'Oct': 10, 'Nov': 11,'Dec': 12}

    
    a = requests.get(url)
    assert a.status_code == 200, "Status code error, Maybe website is down?"
    b = BeautifulSoup(a.content, 'html.parser')

    

   
    temp = b.find_all('a')

    links = []

    for i in temp:
        try:
            if ("/news/" in i['href']):
                links.append(i['href'])

        except:
            pass


    senti = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")
    
    arr_dates = [] # Dates (duh)
    arr_raw = [] # Basically "Header text <ENDOFHEADER> article text"
    arr_0 = [] # Sentiment for header
    arr_1 = [] # Sentiment for first 20% of the article
    arr_2 = [] # Sentiment for end 80% of the article
    
    for node in links:

        raw = ""
        h = BeautifulSoup(requests.get(node).content, 'html.parser') 

        # Dates
        _date = h.find('time').text.replace("\n","").split(" ")[0]

        date = int(datetime.datetime.strptime(_date , '%Y-%m-%d').timestamp())
        
        head = h.find('h1').text

        allp = h.find_all('article')[1].find_all('p')
        s = ""
        for i in allp:
            s += i.text


        raw += head + "<ENDOFHEADER>" + s
        s = s[:511]

        arr_senti = senti([head, s[:int(len(s)*0.2)], s[int(len(s)*0.2):]])

        sh = senti_assign(arr_senti[0])
        s1 = senti_assign(arr_senti[1])
        s2 = senti_assign(arr_senti[2])
        
        arr_dates.append(date)
        arr_raw.append(raw)
        arr_0.append(sh)
        arr_1.append(s1)
        arr_2.append(s2)
        time.sleep(random.randint(1,10) * 0.001)

    data = [[arr_dates[i], arr_raw[i], arr_0[i], arr_1[i],arr_2[i]] for i in range(0,len(arr_dates))]

    news = pd.DataFrame(data, columns=["Datetime", "Text", "Headers", "First20", "Last80"]).sort_values("Datetime",ascending=True)



    name = "dailyfx"
    if len(news) <= 1:
        print(f"Could not find news pair for {name}")
        return news, name

    return news, name
