#graphics.py
# -*- coding: utf-8 -*-

# $Rev: 74 $:  
# $Author: ewald $:  
# $Date: 2022-10-23 15:44:59 +0200 (So, 23. Okt 2022) $:
# $Id: graphics.py 74 2022-10-23 13:44:59Z ewald $ 

__version__ = "$Revision: 74 $"

import pylab
from pylab import  plt, DateFormatter,  getp, setp
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from messaging import errMsg
import sys



class MyAutoDateFormatter(mticker.Formatter): 
    """ 
    This class attempts to figure out the best format to use.  This is 
    most useful when used with the :class:`AutoDateLocator`. 
    """ 
    
    # This can be improved by providing some user-level direction on 
    # how to choose the best format (precedence, etc...) 
    
    # Perhaps a 'struct' that has a field for each time-type where a 
    # zero would indicate "don't show" and a number would indicate 
    # "show" with some sort of priority.  Same priorities could mean 
    # show all with the same priority. 
    
    # Or more simply, perhaps just a format string for each 
    # possibility... 
    
    def __init__(self, locator, tz=None): 
       self._locator = locator 
       self._formatter = DateFormatter("%b %d %Y %H:%M:%S %Z", tz) 
       self._tz = tz 
    
    def __call__(self, x, pos=0): 
        scale = float( self._locator._get_unit() ) 
        #print "Scale =",  scale

        if ( scale == 365.0 ): 
            self._formatter = DateFormatter("%Y", self._tz) 
        elif ( scale == 30.0 ): 
            self._formatter = DateFormatter("%b %Y", self._tz) 
        elif ( (scale == 1.0) or (scale == 7.0) ): 
            self._formatter = DateFormatter("%a %b %d\n %Y", self._tz) 
        elif ( scale == (1.0/24.0) ): 
            self._formatter = DateFormatter("%a %b %d %Y\n%H:%M:%S", self._tz) 
        elif ( scale == (1.0/(24*60)) ): 
            self._formatter = DateFormatter("%a %b %d %Y\n%H:%M:%S", self._tz) 
        elif ( scale == (1.0/(24*3600)) ): 
          self._formatter = DateFormatter("%a %b %d %Y\n%H:%M:%S", self._tz) 
        else: 
            self._formatter = DateFormatter("%a %b %d %Y\%H:%M:%S", self._tz) 
    
        return self._formatter(x, pos)

def my_2D_plot_of_lists(xlist, ylist):
    pylab.plot(xlist, ylist,label='blau',markersize=2  )
    pylab.xlabel('time')
    pylab.ylabel('consumption')
    pylab.title('Consumption over time')
    pylab.grid(True)
    pylab.show()
    

    
def check_add_graphs(args):
    gi=1
    #check correct number of arguments
    if ( len(args)%3 != 0):
        errMsg( 'Wrong number of arguments (not multiple of 3): %d\nExiting because of a fatal error!\n' % len(args))
        errMsg('\nPassed arguments were:\n')
        for i in args: 
            print ( i )
        sys.exit(1)
    #check dimensions of arrays
    for j in range(0, len(args), 3):
        gi=gi+1
        if ( len(args[j]) != len(args[j+1])  ):
            errMsg( 'Dimensions of input arrays of graph %d do not match: %d versus %d\nExiting because of a fatal error!\n' % (gi,  len(args[j]),  len(args[j+1])))
            sys.exit(1)
    #TODO: check for correct format string
        
def   draw_add_2D_plot_of_arrays(add_graphs,  ax):
# plot additional graphs
    
    check_add_graphs(add_graphs)
    for j in range(0, len(add_graphs), 3):
        ax.plot(add_graphs[j], add_graphs[j+1], add_graphs[j+2])
        
        
def my_2D_plot_of_arrays(xa, ya, title, xlabel, ylabel,  *add_graphs):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    lines=ax.plot(xa, ya, 'b-o',  markersize=2)

    line = lines[0]
    
    line.set_linewidth( 1.5 )
    line.set_color( 'green' )
    line.set_linestyle( '-' )
    line.set_marker('s')
    line.set_markerfacecolor('red')
    line.set_markeredgecolor( '0.1' ) 
    line.set_markersize( 3 ) 
    
    ## format the ticks
    adl = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(adl)
    myformatter = MyAutoDateFormatter(adl)
    #myformatter = mdates.AutoDateFormatter(adl)
    ax.xaxis.set_major_formatter(myformatter)
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    labels = getp(ax, 'xticklabels')
    setp(labels, color='g', fontsize=9, fontname="Verdana" )
    labels = getp(ax, 'yticklabels')
    setp(labels, color='g', fontsize=9, fontname="Verdana" )
    
    
    ax.grid(True)
    fig.autofmt_xdate(bottom=0.18,  rotation=60)
    
    min_y=min(ya)
    max_y=max(ya)
    if (min_y<0) and (max_y >0):
        ax.axhline(0, color='r', lw=4, alpha=0.5)
        ax.fill_between(xa, ya, facecolor='red',  alpha=0.5, interpolate=True)

    #plot additional graphs
    if len(add_graphs):
        draw_add_2D_plot_of_arrays(add_graphs, ax)
        
    plt.show()
    



 
    

