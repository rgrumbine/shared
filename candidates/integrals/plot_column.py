import sys
import os
import numpy as np
import datetime
from math import *
import copy

import netCDF4
import matplotlib
import matplotlib.pyplot as plt

'''

'''

#------------------------------------------------
matplotlib.use('Agg')
fig,ax = plt.subplots()

start  = 1
end    = 60

col = int(sys.argv[1])
k = 0
for f in sys.argv[2:]:
  vector = np.zeros((int((8784-24)/24)+2 ))
  days   = np.zeros(len(vector))
  fin = open(f, "r")
  for line in fin:
    words = line.split()
    #debug: print(words[1],words[col], flush=True)
    #debug: print(int(float(words[1])), flush=True)
    vector[int(float(words[1]))] += float(words[col])
    days[int(float(words[1]))] = int(float(words[1]))

  vector /= 10
  ax.plot(days[1:], vector[1:], label = "expt"+"{:d}".format(k) )
  k += 1

have = False
if (col == 6):
  fin_nsidc = open("sh.nsidc.20231101","r")
  have = True
elif (col == 5):
  fin_nsidc = open("nh.nsidc.20231101","r")
  have = True
print("have = ",have)
  
if (have):
  vector = np.zeros((int((8784-24)/24)+2 ))
  i = 1
  for line in fin_nsidc:
    words = line.split()
    vector[i] = float(words[0])
    i += 1
  ax.plot(days[1:], vector[1:], label = "nsidc", color = "black")

ax.legend()
ax.grid()
plt.savefig("overlay.png")
