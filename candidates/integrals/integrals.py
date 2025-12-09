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

#import sys
import os
import datetime
import copy

import numpy as np
from numpy import ma
import netCDF4
import matplotlib
import matplotlib.pyplot as plt

# Edit these ----------------------------------------------------------
base   = '/ncrc/home1/Robert.Grumbine/scratch6/COMROOT/'
start  = datetime.datetime(2023,11,1)
expt   = 'icein5'
maxmem = 10
#maxhour = 8784
maxhour = 744
crit_conc = 0.15 #concentration defining 'extent'

# Should not need editing below here ----------------------------------
def find_extent(cellarea, conc, crit):
  '''
  Find the ice extent for a given critical concentration
  '''
  total = 0.

  # very slow and requires shape info
  #nj = 320
  #ni = 360
  #for jj in range(0,nj):
  #  for ii in range(0,ni):
  #    if (conc[jj,ii] > crit):
  #      total += cellarea[jj,ii]

  # about 14x faster than above
  mask = ma.masked_array(conc >= crit)
  indices = mask.nonzero()
  for k in range(0,len(indices[0])):
    jj = indices[0][k]
    ii = indices[1][k]
    total += cellarea[jj,ii]

  return total

#------------------------------------------------
matplotlib.use('Agg')
fig,ax = plt.subplots()

area   = np.zeros((int((maxhour-24)/24)+2 ))
extent = np.zeros((int((maxhour-24)/24)+2 ))
nhext  = np.zeros((int((maxhour-24)/24)+2 ))
shext  = np.zeros((int((maxhour-24)/24)+2 ))
volume = np.zeros((int((maxhour-24)/24)+2 ))
days   = np.zeros(len(area))

for memno in range(0,maxmem+1):
#for memno in range(0,2):
#debug: memno  = 0

  fbase = base + expt + '/sfs.' + start.strftime("%Y%m%d") + '/00/mem' + \
               f"{memno:03d}"+'/model/ice/history/sfs.t00z.24hr_avg.f'
               #f"{memno:03d}" + '/products/ice/netcdf/native/sfs.t00z.tripolar.f'

  for h in range(24,maxhour+1,24):
    fname = fbase + f"{h:03d}" + '.nc'
    if (not os.path.exists(fname)):
        print("no such file ",fname)
        #sys.exit(1)
        continue
    model = netCDF4.Dataset(fname)
    if (h == 24 and memno == 0):
      tlat = model.variables['TLAT'][:,:]
      #tarea *= np.cos(tlat*pi/180.)
      fhistory = base + expt + '/sfs.' + start.strftime("%Y%m%d") + '/00/mem' + \
              f"{memno:03d}"+'/model/ice/history/sfs.t00z.24hr_avg.f024.nc'
      grid = netCDF4.Dataset(fhistory)
      tarea = grid.variables['tarea'][:,:]
      del grid
      tarea /= 1e12
      #debug: print("tarea ",tarea.max(), tarea.min() )
      #debug: sys.exit(0)

      nharea = copy.deepcopy(tarea)
      nharea[tlat < 0] = 0.
      sharea = copy.deepcopy(tarea)
      sharea[tlat > 0] = 0.
      #debug: print("nh, sh area",nharea.max(), sharea.max(), nharea.shape )
      #debug: sys.exit(0)

    hi = model.variables['hi_h'][0,:,:]
    ai = model.variables['aice_h'][0,:,:]

    i = int(h/24)
    days[i] = h/24

    tmp       = ai*tarea
    area[i]   = tmp.sum()
    tmp2 = hi*tmp
    volume[i] = tmp2.sum()
    #debug: sys.exit(0)

    #extent[i] = tarea[ ai > crit_conc ].sum()
    #extent[i] = find_extent(tarea, ai, crit_conc)
    #debug: print(days[i], area[i], volume[i], extent[i], flush=True)
    nhext[i] = find_extent(nharea, ai, crit_conc)
    shext[i] = find_extent(sharea, ai, crit_conc)
    extent[i] = nhext[i] + shext[i]
    print(memno, days[i], area[i], volume[i], extent[i], nhext[i], shext[i], flush=True )

  if (memno == 0):
    ax.plot(days[1:], area[1:], color = 'red', label = 'area')
    ax.plot(days[1:], extent[1:], color = 'blue', label = 'extent')
    ax.plot(days[1:], nhext[1:], color = 'blue', label = 'nhext')
    ax.plot(days[1:], shext[1:], color = 'blue', label = 'shext')
    ax.plot(days[2:], volume[2:], color = 'black', label = 'volume')
  else:
    ax.plot(days[1:], area[1:], color = 'red')
    ax.plot(days[1:], extent[1:], color = 'blue')
    ax.plot(days[1:], nhext[1:], color = 'blue')
    ax.plot(days[1:], shext[1:], color = 'blue')
    ax.plot(days[2:], volume[2:], color = 'black')


ax.legend()
ax.grid()
plt.savefig("out"+expt+".png")
