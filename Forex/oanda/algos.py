from datetime import datetime
import random
import time
from utils import log

def fify_fify(env, settings, start_time):
    endtime = start_time + settings['Trade Duration']


    ctime = datetime.now().timestamp()



    pairs = list(settings['Pair Settings'].keys())
    brain = {}
    # Initializes the randomness of the pairs
    for i in pairs:
        r = random.random()
        if r < settings['coef']:
            brain[i] = 1
        else:
            brain[i] = -1
        brain[i + 'count'] = 0

    pair_settings = settings['Pair Settings']

    s = f"[CLOSED] All Pairs PL {env.close_all()}"
    print(s)
    log(s)

    ###### Start main loop #####


    while ctime < endtime:

        pls = env.get_pl()
        for p in pair_settings.keys():
            
            # Loads settings
            if settings['General Settings'] == "true":
                units = settings['units'] * brain[p]       
                take_stop = settings['sltp']
                count = settings['count']
            else:
                units = settings[p]['units'] * brain[p] 
                take_stop = settings[p]['sltp']
                count = settings[p]['count']
            
            if p not in pls.keys():
                env.buy_sell(p,units,take_stop)
                
                s = f"[{('BUY' if units > 0 else 'SELL')}] {p} U {units}"
                print(s)
                log(s)
            elif pls[p] > 0 or brain[p + "count"] >= count:
                log(f"[CLOSE] {p} PL {env.close(p)} U {units}")
                brain[p] *= -1
                brain[p + "count"] = 0
                env.buy_sell(p, units*brain[p], take_stop)
            else:
                brain[p + "count"] += 1
        
        totalpl = sum(pls[i] for i in pls.keys())
        
        percs = (ctime - start_time) / (settings['Trade Duration']) * 100 
        print(f"[STEP] {percs:.2f} PL {totalpl}")
        log(f"[STEP] {percs:.2f} PL {totalpl}")
        time.sleep(settings['Trade Interval'])

        ctime = datetime.now().timestamp()


    log(f"[END] {env.close_all()}")

    return 0
    ##### End Main Loop #####