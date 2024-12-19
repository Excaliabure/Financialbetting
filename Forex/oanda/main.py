import os
import time
import random
from forex import *
from datetime import datetime
from algos import fify_fify, second_deriv

os.system('clear' if os.name != 'nt' else 'cls')
env = ForexApi()
env.log_info()
start_time, settings = start()


##### Start of Logic #####

second_deriv(env,settings,start_time)

##### End of Logic #####

env.close_all()
end(start_time)
