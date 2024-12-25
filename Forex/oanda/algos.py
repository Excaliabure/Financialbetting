from datetime import datetime
import random
import time
from utils import log, smooth_ma
from forex import *

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


def algo_deriv(env,settings,start_time, ret_derivs=False):


        # Preprocessing
    # Close, High, Low, Open







    # y = y[2:]
    # dy = deriv(y)
    # ddy = deriv(deriv(y))

    # f, axes = plt.subplots(3,1, figsize=(5,5))
    # axes[0].plot(y, label='y')
    # # axes[0].plot(y_prev, label='y_prev')
    # axes[1].plot(dy)
    # axes[2].plot(ddy)
    # plt.show()

    # Initial Buy sell position placing


    history_arr_dict = {}
    for pair in settings['Pair Settings'].keys():
        weights = np.array([0,0,0.8,0.1,0.1,0])
        fx = forex(pair)
        history_arr = fx.min.iloc[1:,1:].to_numpy(dtype=float) @ weights
        val = float(env.get_pair(pair)['prices'][0]['bids'][0]['price'])
        
        history_arr = np.append(history_arr, val)
        y = np.array(history_arr)
        iters = settings['Iterations']
        c = 0
        y = smooth_ma(y[len(y) - 30 : ], 3)
        ddy = deriv(deriv(y))
        hold_position = -1 if ddy[-3] < 0 else 1
        current_position = hold_position

        # env.close(pair)
        # env.buy_sell(pair, 1000 * current_position, 999, terminal_print = False)

        history_arr = history_arr.tolist()
        history_arr_dict[pair] = {}
        history_arr_dict[pair]["history_arr"] = history_arr
        history_arr_dict[pair]["hold_position"] = hold_position
        history_arr_dict[pair]["current_position"] = current_position
        history_arr_dict[pair]["hold_times"] = 2
        print(f"Put a {'Sell' if current_position == -1 else 'Buy'} position on {pair}")
        time.sleep(0.5)



    while c < iters:

        for pair in settings['Pair Settings'].keys():

            current_position = history_arr_dict[pair]["current_position"]
            hold_position = history_arr_dict[pair]["hold_position"]
            sltp = settings['Pair Settings'][pair]["sltp"]
            tol = settings['tolerance']


            val = float(env.get_pair(pair)['prices'][0]['bids'][0]['price'])
            
            history_arr = np.array(history_arr_dict[pair]["history_arr"])
            history_arr = np.append(history_arr, val)
            y = smooth_ma(history_arr, 3)
            history_arr_dict[pair]["history_arr"] = history_arr.tolist()


            y = y[2:]
            dy = deriv(y)
            ddy = deriv(deriv(y))
            
            ddy_avg = ddy.mean()
            d1 = ddy[-1]

            # if ddy is 0, thats min/max
            # if that is case, check deriv if positive, sell pos if neg but pos
            switchup = abs(ddy[-1]) > (0 + abs(ddy.max()) * tol)

            # hold_position = 1 if dy[-1 0 + ddy.max() * tol
            if switchup:
                if (dy[-1] < 0):
                    hold_position = 1
                elif (dy[-1] > 0):
                    hold_position = -1

            hold_time = -1
            if ret_derivs:
                return y,dy,ddy
            
            if current_position != hold_position:
                
                # q = env.close(pair)
                print(f"{pair} closed {q}")
                
                current_position = hold_position
                time.sleep(0.5)
                
                # env.buy_sell(pair, 1000 * current_position, sltp, terminal_print=False)
                print(f"{'\n[SELL]' if hold_position == -1 else '[BUY]'} position on {pair} with deriv = {ddy[-1]}\n")
                time.sleep(0.5)




            history_arr_dict[pair]["current_position"] = hold_position
            history_arr_dict[pair]["hold_position"] = hold_position
            if (env.view(pair) == None):
                print(f"\nNo sell/buy position for {pair}. Attempting...")
                tempcurr = history_arr_dict[pair]["current_position"]
                # env.buy_sell(pair, 1000 * tempcurr, sltp, terminal_print=False)
                print(f"{'[SELL]' if hold_position == -1 else '[BUY]'} position on {pair} with deriv = {ddy[-1]}\n")

            print(f"y : {y[-1]} | dy : {dy[-1]} | ddy {ddy[-1]}")

                
            c += 1


        time.sleep(30.5)
