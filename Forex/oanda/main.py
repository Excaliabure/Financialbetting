import os
import time
import random
from forex import *
from datetime import datetime
from algos import fify_fify

os.system('clear' if os.name != 'nt' else 'cls')
env = ForexApi()
env.log_info()
start_time, settings = start()


##### Start of Logic #####

trade_interval = settings['Trade Interval']
ctime = datetime.now().timestamp()
pair_settings = settings['Pair Settings']


while ctime < start_time:


    # mline,sline,histo = env.get_macd('EUR_USD')
    for pair in pair_settings.keys():
        pair_setting = pair_settings[pair]
        units = pair_setting['units']
        sltp = pair_setting['sltp']
        count = pair_setting['count']


        lm,sm,cm= env.get_ema_cross(pair)
        x = sm - lm
        
    # If cross is positive for 


    time.sleep(trade_interval)
    ctime = datetime.now().timestamp()


##### End of Logic #####

env.close_all()
end(start_time)
