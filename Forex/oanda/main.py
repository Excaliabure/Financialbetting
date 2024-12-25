import os
import time
import random
from forex import *
from datetime import datetime
from algos import *

os.system('clear' if os.name != 'nt' else 'cls')
env = ForexApi()
env.log_info()
start_time, settings = start()


##### Start of Logic #####

algo_deriv(env,settings,start_time)

##### End of Logic #####

env.close_all()
end(start_time)
