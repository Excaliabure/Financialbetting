from stocks import *
from gymnasium.spaces import Discrete, Box 
import random


class Market():

    def __init__(self, tick,ttype="min", amt=1000,add_sentiment=False ):

        """ This struct only works for USD accounts and USD/*** or ***/USD pairs 
            
        :params
            pair - Any type of pair, must have the format of "NAMENAME", ex EURUSD
            amt - amount of starting money
            ttype - what the env is going to use, aka day, hour, or min   

        """
        self.tick = tick
        t = stocks(tick)
        if (add_sentiment == True):
            t.add_senti()

        if (ttype == "day"):
            self.arr = t.day.to_numpy()
        elif (ttype == "hour"):
            self.arr = t.hr.to_numpy()
        else:
            self.arr = t.min.to_numpy()

    
        self.arr_close = self.arr[:,4:5].squeeze()
        self.arr_mean = [sum(i)/4 for i in self.arr]

        leverage_dict = {"GBPUSD" : 20,
                        "EURUSD" : 50}

        # Main vars
        self.reset_funds = amt
        self.funds = amt
        self.avali = self.funds
        self.margin = 0
        self.pl = 0
        self.idx = 0

        # Calulation vars
        self.leverage = leverage_dict[self.tick]
        self.opening = 0
        self.lot_size = 0
        self.lot_size_additional = 0
        self.latest = self.arr_close[1]

        # Env vars
        self.statcalls = 0
        # Calculation functions
        # Works
        self.pl_fn = lambda _open,_close,lot : (_close-_open) * lot * 1e6
        # Works
        self.new_opening_fn = lambda opening, closing, lot_size, additional_lot: ((lot_size * opening) + (additional_lot * closing)) / (lot_size + additional_lot) if (round(lot_size + additional_lot,3) != 0) else 0
        # Works for all non jpy pairs
        self.margin_cost_fn = lambda opening,leverage, lot_amt :  (100000 * opening / leverage * lot_amt) if lot_amt != 0 else 0

        # Vars for RL part
        self.action_space = Discrete(4)
        self.observation_space = Box(low=self.arr.min(), high=self.arr.max())
        self.state = self.arr[0]

    def close(self):
        self.avali += abs(self.margin) + self.pl
        self.funds = self.avali
        self.margin = 0
        self.pl = 0
        self.lot_size = 0
        self.lot_size_additional = 0
        self.opening = 0
        self.latest = 0
    
    def buy_sell(self, amt=1):
        self.opening = (self.latest if self.opening == 0 or self.lot_size == 0 else self.opening)
        self.lot_size_additional = round(0.01*amt,3)

        opening_new = self.new_opening_fn(self.opening, self.latest, self.lot_size, self.lot_size_additional)
        margin_i = self.margin
        margin_c = self.margin_cost_fn(self.opening,self.leverage,self.lot_size_additional)

        # Acts like a hold since cant buy any
        if (margin_c > self.avali):
            pass
        # If in favor
        elif ((self.lot_size >= 0 and self.lot_size_additional > 0) or (self.lot_size <= 0 and self.lot_size_additional < 0)):
      
            self.avali -= abs(margin_c)
            self.margin += abs( margin_c)
            self.lot_size += self.lot_size_additional
            self.opening = opening_new

        # If goes beyond negative, close
        elif (self.lot_size + self.lot_size_additional == 0 or (self.lot_size + self.lot_size_additional < 0 and self.lot_size > 0) or (self.lot_size + self.lot_size_additional > 0 and self.lot_size < 0)):
            
            self.avali += abs(self.margin) + self.pl
            self.funds = self.avali
            self.margin = 0
            self.pl = 0
            self.lot_size = 0
            self.lot_size_additional = 0
            self.opening = 0
            self.latest = 0

        # If not in favor (i believe works)
        else:

            self.avali += abs(margin_c)
            self.margin -= abs( margin_c)
            self.lot_size += self.lot_size_additional
            self.lot_size = round(self.lot_size,3)
            self.opening = opening_new
    
    def step(self,action=0, steps=1):
        # buy,sell,hold,close 
        if action == 0:
            self.buy_sell(1)
        elif action == 1:
            self.buy_sell(-1)
        elif action == 3:
            self.close()

        self.idx += steps
        self.latest = self.arr_close[self.idx]
        self.margin = abs(self.margin)
        self.pl = self.pl_fn(self.opening,self.latest,self.lot_size)

        # RL
        self.state = self.arr[self.idx]
        
        reward = self.pl# * 4
        done = (True if self.idx == len(self.arr)-2 or self.avali + self.margin + self.pl  < 400 else False)
     
        info = {}
        return self.state, reward, done, info

    def reset(self,random_start=False):
        self.funds = self.reset_funds
        self.avali = self.funds
        self.margin = 0
        self.pl = 0
        self.idx = 1
        self.opening = 0
        self.lot_size = 0
        self.lot_size_additional = 0
        self.latest = self.arr_close[1]
        self.state = self.arr[0]
        info = {}
        if (random_start == True):
            self.idx = int(random.random() * (len(self.arr)/2))

        self.statcalls = 0
        return np.array(self.state), info
    
    def __len__(self):
        return len(self.arr)
        

    def stats(self):
        self.statcalls += 1
        print(f"{self.statcalls}.\nAvailable : {self.avali}")
        print(f"Margin: {self.margin}")
        print(f"Pl : {self.pl}")
        print(f"Position : {self.lot_size}")
        print(f"Funds : {self.funds}")
        print(f"Opening : {self.opening}")
        print(f"Latest : {self.latest}")
        print(f"Idx : {self.idx}")
        print("\n")
    
    def getlast(self):
        return self.arr[-1]

