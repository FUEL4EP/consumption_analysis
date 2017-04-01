#/usr/bin/env python
# -*- coding: utf-8 -*-

# $Rev: 59 $:  
# $Author: ewald $:  
# $Date: 2016-09-17 12:30:39 +0200 (Sa, 17. Sep 2016) $:
# $Id: verbrauch.py 59 2016-09-17 10:30:39Z ewald $ 

__version__ = "$Revision: 59 $"

import os 
import pylab
from scipy import linspace, polyval, polyfit, sqrt, stats, randn, interpolate
import numpy
from numpy import *
from pylab import *
import time
import datetime
import matplotlib.dates as mdates
import matplotlib.mlab as mlab


def smooth(x,window_len=365,window='flat'):
    """smooth the data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal 
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.
    
    input:
        x: the input signal 
        window_len: the dimension of the smoothing window
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal
        
    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)
    
    see also: 
    
    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter
 
    TODO: the window parameter could be the window itself if an array instead of a string   
    """

    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


#    s=numpy.r_[2*x[0]-x[window_len:1:-1],x,2*x[-1]-x[-1:-window_len:-1]

    s=numpy.r_[x]
    
#    pylab.plot(s,label='green')
#    pylab.show()
#    
   
    
    if window == 'flat': #moving average
        w=ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    return y



working_dir="/home/ewald/CAD/python/_work/consumption_analysis"
input_file="verbrauch.txt"
consumption_file=working_dir+'/'+input_file
print 'Die Verbrauchsdaten stehen in ' + consumption_file

#read file with consumption values, space separated time, consumption

time_list=[]
consumption_list=[]
i=0
try:
    fobj=open(consumption_file, 'r')
    for eachLine in fobj:  
        eachLine = eachLine.rstrip() 
        i+=1
        parts=eachLine.split()
        time_list.append(float(parts[0]))
        consumption_list.append(float(parts[1]))
    fobj.close()
    
except IOError,  e:
    print 'file open error:', e

#Linear regressison -polyfit - polyfit can be used other orders polys
(ar,br)=polyfit(time_list,consumption_list,1)
consumption_list_r=polyval([ar,br],time_list)
#compute the mean square error
err=sqrt(sum((consumption_list_r-consumption_list)**2)/len(consumption_list))

print('\nLinear regression using polyfit')
print('\nregression: \nslope a=%.2f\noffset b=%.2f\nmean square error= %.3f\n\n' % (ar,br,err))

    
pylab.plot(time_list, consumption_list,label='blau')
pylab.plot(time_list,consumption_list_r,label='red')
pylab.xlabel('time')
pylab.ylabel('consumption')
pylab.title('Consumption over time')
pylab.grid(True)
pylab.show()

delta_consumption_list=[]
delta_time_list=[]
for j in range(len(time_list)-1):
    delta=(consumption_list[j+1]-consumption_list[j])/(time_list[j+1]-time_list[j])
    delta_consumption_list.append(delta)
    delta_time_list.append(time_list[j+1])
    
pylab.plot(delta_time_list, delta_consumption_list,label='red')
pylab.xlabel('time')
pylab.ylabel('delta_consumption')
pylab.title('Consumption over time')
#pylab.grid(True)
pylab.show()

tmin=min(time_list)
tmax=max(time_list)

time_step=0.5

equidistant_time_list=numpy.arange(tmin, tmax, time_step)
#print equidistant_time_list[-1]

rep = interpolate.splrep(time_list,consumption_list, k=1)
interpolated_consumption_list=interpolate.splev(equidistant_time_list,rep)

pylab.plot(equidistant_time_list, interpolated_consumption_list,label='green')
pylab.xlabel('equidistant sampled time')
pylab.ylabel('interpolated consumption')
pylab.title('Interpolated Consumption over time')
pylab.grid(True)
pylab.show()


print "\n\nVerbrauch im letzten Jahr: ",  interpolated_consumption_list[-1]-interpolated_consumption_list[-365*2-1]
print "\nVerbrauch im vorletzten Jahr: ",  interpolated_consumption_list[-365*2-1]-interpolated_consumption_list[-365*4-1]
print "\nVerbrauch im vorvorletzten Jahr: ",  interpolated_consumption_list[-365*4-1]-interpolated_consumption_list[-365*6-1]


delta_interpolated_consumption_list=[]
delta_equidistant_time_list=[]
for j in range(len(equidistant_time_list)-1):
    delta_eq=(interpolated_consumption_list[j+1]-interpolated_consumption_list[j])/(equidistant_time_list[j+1]-equidistant_time_list[j])
    delta_interpolated_consumption_list.append(delta_eq)
    delta_equidistant_time_list.append(equidistant_time_list[j+1])
    
pylab.plot(delta_equidistant_time_list, delta_interpolated_consumption_list,label='green')
pylab.xlabel('time')
pylab.ylabel('delta_consumption of interpolated values')
pylab.title('Consumption over time of interpolated values')
#pylab.grid(True)
pylab.show()

wlen=int(365/time_step)

dicl=numpy.array(delta_interpolated_consumption_list)
smoothened_delta_consumption_list=smooth(dicl, window_len=wlen)
detl=numpy.array(delta_equidistant_time_list[wlen-1:])
print smoothened_delta_consumption_list.shape, detl.shape
pylab.plot(detl, smoothened_delta_consumption_list,label='green')

xmgrace_date_offset = datetime.datetime(1970, 1, 1, 0, 0, 0)
print "Epoch Seconds:", time.mktime(xmgrace_date_offset.timetuple())
print "local time offset to UTC", time.timezone
print time.tzname

pylab.xlabel('time')
pylab.ylabel('moving average of consumption')
pylab.title('1 year moving average of consumption')
#pylab.grid(True)
pylab.show()

years    = mdates.YearLocator()   # every year
months   = mdates.MonthLocator()  # every month
yearsFmt = mdates.DateFormatter('%Y')
#print detl
#detlo=matplotlib.dates.epoch2num(detl)
#print detlo
#
cbd=datetime.datetime(1970, 1, 1, 1, 0, 0)-datetime.datetime(1, 1, 1, 1, 0, 0)
print "cbd.days",  cbd.days
detl=detl+cbd.days
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(detl, smoothened_delta_consumption_list)

## format the ticks
ax.xaxis.set_major_locator(years)
ax.xaxis.set_major_formatter(yearsFmt)
ax.xaxis.set_minor_locator(months)

plt.show()

