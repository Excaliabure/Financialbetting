from forex import *
from utils import *
from update import *


usr = input("Input pair to update: ")

z = forex(str(usr))
z.update()

