# from forex import forex, ForexApi

# a = ForexApi()

import numpy as np
from scipy.integrate import simpson
from matplotlib.pyplot import *

a = np.linspace(0,3.7,num=1000) ** 4

def integ(arr):

    temp = []

    for i in range(1,len(arr)):
        temp.append( (arr[i-1] + arr[i]) )

    return np.array(temp)/2

print(a[-1])
print(integ(a)[-1])

plot(a)