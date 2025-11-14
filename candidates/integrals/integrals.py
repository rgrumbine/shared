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
Integral statistics for sea ice -- area, extent, volume

edit 'base' to point to the directory above the experiments
  edit starting date 
  then provide experiment name(s)
assumes cycle = 00
assumes members 000-010
sfs.20231101/00/mem000/products/ice/netcdf/native
all hours f024 to f8784

needs auxiliary file with tarea for the cells

'''

# Edit these
base   = '/ncrc/home1/Robert.Grumbine/scratch6/COMROOT/'
start  = datetime.datetime(2023,11,1)
expt   = 'evo1b'
maxmem = 10
crit_conc = 0.15 #concentration defining 'extent'

tarea = np.ones((320,360)) #j,i
tarea *= 55*111.2/1.e6

# Should not need editing below here
def find_extent(tarea, ai, crit_conc):
  total = 0.
  nj = 320
  ni = 360

  for j in range(0,nj):
    for i in range(0,ni):
      if (ai[j,i] > crit_conc): total += tarea[j,i]

  return total

# for memno in range(0,maxmem):
memno  = 0
area   = np.zeros((int((8784-24)/24)+2 ))
extent = np.zeros((int((8784-24)/24)+2 ))
nhext  = np.zeros((int((8784-24)/24)+2 ))
shext  = np.zeros((int((8784-24)/24)+2 ))
volume = np.zeros((int((8784-24)/24)+2 ))
days   = np.zeros(len(area))

fbase = base + expt + '/sfs.' + start.strftime("%Y%m%d") + '/00/mem'+"{:03d}".format(memno)+'/products/ice/netcdf/native/sfs.ice.t00z.native.f'

for h in range(24,8784+1,24):
  fname = fbase + "{:03d}".format(h) + '.nc'
  if (not os.path.exists(fname)):
      print("no such file ",fname)
      exit(1)
  model = netCDF4.Dataset(fname)
  if (h == 24):
    tlat = model.variables['TLAT'][:,:]
    tarea *= np.cos(tlat*pi/180.)
    nharea = copy.deepcopy(tarea)
    nharea[tlat < 0] = 0.
    sharea = copy.deepcopy(tarea)
    sharea[tlat > 0] = 0.
    print("nh, sh area",nharea.max(), sharea.max(), nharea.shape )

  hi = model.variables['hi_h'][0,:,:]
  ai = model.variables['aice_h'][0,:,:]

  i = int(h/24)
  days[i] = h/24

  tmp = ai*tarea
  area[i]   = tmp.sum() 
  volume[i] = (hi*tmp).sum()

  #extent[i] = tarea[ ai > crit_conc ].sum()
  extent[i] = find_extent(tarea, ai, crit_conc)
  #print(days[i], area[i], volume[i], extent[i])
  nhext[i] = find_extent(nharea, ai, crit_conc)
  shext[i] = find_extent(sharea, ai, crit_conc)
  print(days[i], area[i], volume[i], extent[i], nhext[i], shext[i] )

matplotlib.use('Agg')
fig,ax = plt.subplots()
ax.plot(days, area, color = 'red', label = 'area')
ax.plot(days, extent, color = 'blue', label = 'extent')
ax.plot(days, nhext, color = 'blue', label = 'nhext')
ax.plot(days, shext, color = 'blue', label = 'shext')
ax.plot(days, volume, color = 'black', label = 'volume')
ax.legend()
ax.grid()
plt.savefig("out"+expt+".png")

