from stocks import *
from utils import *
from update import *


usr = input("Input pair to update: ")

z = stocks(str(usr))
z.update()

