'''
Plot multiple files' given column number.
If 5 or 6 (nhextent and shextent, respectively) also plot nsidc extents
'''

import sys

import numpy as np

import matplotlib
import matplotlib.pyplot as plt

#------------------------------------------------
matplotlib.use('Agg')
fig,ax = plt.subplots()

start  = 1
end    = 31
maxhrs = end*24+24

col = int(sys.argv[1])
k = 0
for f in sys.argv[2:]:
  vector = np.zeros((int((maxhrs)/24)+2 ))
  days   = np.zeros(len(vector))
  fin = open(f, "r", encoding='utf-8')
  for line in fin:
    words = line.split()
    #debug: print(words[1],words[col], flush=True)
    #debug: print(int(float(words[1])), flush=True)
    vector[int(float(words[1]))] += float(words[col])
    days[int(float(words[1]))] = int(float(words[1]))

  vector /= 10
  ax.plot(days[1:end], vector[1:end], label = "expt"+f"{k:d}" )
  k += 1

have = False
if (col == 6):
  fin_nsidc = open("sh.nsidc.20231101","r", encoding='utf-8')
  have = True
elif (col == 5):
  fin_nsidc = open("nh.nsidc.20231101","r", encoding='utf-8')
  have = True
print("have = ",have)

if (have):
  vector = np.zeros((int((maxhrs)/24)+2 ))
  i = 1
  for line in fin_nsidc:
    words = line.split()
    vector[i] = float(words[0])
    i += 1
    if (i > end):
        break
  ax.plot(days[1:end], vector[1:end], label = "nsidc", color = "black")

ax.legend()
ax.grid()
plt.savefig("overlay.png")
