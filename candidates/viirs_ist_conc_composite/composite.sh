#!/bin/sh

module load prod_envir

# Environment to run: COMOUT, DCOMROOT, PDY, PDYm1, PDYm2, cyc
#                     EXECseaice_analysis
# COMOUT = directory you want the output in
# DCOMROOT = set by module prod_envir
# PDY = 'today'
# PDYm1 = 'yesterday'
# PDYm2 = 'day before yesterday'
# ... the PDY are and relationship to cycles is set by NCEP operations.
# cyc = the cycle you want -- 00, 06, 12, 18
# EXECseaice_analysis = directory with compositing python
#
# Also it assumed that you have a python environment established in your 
#   home directory, and that you're running python 3.12
#
# Robert Grumbine

set -x
set -e

source $HOME/env3.12/bin/activate
export PYTHONPATH=$PYTHONPATH:/lfs/h2/emc/couple/save/rg/rgops/mmablib/py

day=$PDY
if [ $cyc == '00' ] ; then
  hours='10 09 08 07 06 05'
elif [ $cyc == '06' ] ; then
  hours='16 15 14 13 12 11'
elif [ $cyc == '12' ] ; then
  hours='22 21 20 19 18 17'
elif [ $cyc == '18' ] ; then
  day=$PDYm1
  hours='04 03 02 01 00' #handle 23 separately, PDYm2
else
  echo exseaice_viirs: illegal cycle $cyc, exiting
  exit 1
fi


echo zzzzz working on viirs $PDY cycle=$cyc
for inst in j01 npp n21
do
  for hh in $hours
  do
    python3 $EXECseaice_analysis/composite.py \
    $DCOMROOT/$day/wgrdbul/IST/JRR-IceConcentration*_${inst}_s${day}${hh}*.nc \
    > viirs.$inst.$cyc.${day}$hh 
    # Handle no file case 
    if [ ! -f viirs.$inst.$cyc.${day}$hh ] ; then
      touch viirs.$inst.$cyc.${day}$hh
    fi
  done
done

# special case for 23z
if [ $cyc == '18' ] ; then
  day=$PDYm2
  hours='23'
  for inst in j01 npp n21
  do
    for hh in $hours
    do
      python3 $EXECseaice_analysis/composite.py \
      $DCOMROOT/$day/wgrdbul/IST/JRR-IceConcentration*_${inst}_s${day}${hh}*.nc \
      > viirs.$inst.$cyc.${day}$hh 
      # Handle no file case 
      if [ ! -f viirs.$inst.$cyc.${day}$hh ] ; then
        touch viirs.$inst.$cyc.${day}$hh
      fi
    done
  done
fi


mv viirs.*.$cyc.*?? $COMOUT

