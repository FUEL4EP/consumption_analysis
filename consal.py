#!/usr/bin/env python
# -*- coding: utf-8 -*-

desc="""consal.py is doing a statistical analysis of electrical power,  water, and oil consumptions"""

# $Rev: 61 $:  
# $Author: ewald $:  
# $Date: 2017-04-02 13:06:08 +0200 (So, 02. Apr 2017) $:
# $Id: consal.py 61 2017-04-02 11:06:08Z ewald $ 

__my_version__ = "$Revision: 61 $"


WORKING_DIR="/home/ewald/CAD/python/_work/consumption_analysis"
ELECTRICAL_POWER_CONSUMPTION_FILE="electrical_power_consumption.caf"
WATER_CONSUMPTION_FILE="water_consumption.caf"
OIL_CONSUMPTION_FILE ="oil_consumption.caf"
TIME_COL=0
VALUE_COL= 1
STRICTLY_INCREASING=1
NOT_STRICTLY_INCREASING=0
MOVING_AVERAGE_DAYS=365
RESAMPLE_TIME_STEP=0.25
EPSILON=1e-6
MAX_MEASUREMENT_VARIATION=4

import sys  

import os
from scipy import stats, interpolate
import numpy
import scipy
import time
import datetime
from messaging import stdMsg, warnMsg, errMsg, setDebugging
import messaging
import graphics
from io_module import  check_working_directory,  check_database_file,  input_float

setDebugging(0)

def remove_CR_LF_form_list(list):
    j=0
    for row in list:
        list[j]=row.rstrip("\r\n")
        j+=1
    return list
    
    
class consumption(object):
    """ 
    
    """

    def __init__(self):
        """ Initialise the consumption object."""
        self.name=''
        self.wd=''
        self.table_name=''
        self.write_table_name=''
        self.table=[]
        self.np=0
        #list
        self.tl=[]
        self.cl=[]
        #numpy array
        self.ta=[]
        self.ca=[]
        #dictionary
        self.cda={}
        #numpy array at equidistant time steps RESAMPLE_TIME_STEP
        self.edta=[]
        self.edca=[]
        #moving average array
        self.edmata=[]
        self.edmaca=[]
        #delta moving average array
        self.dedmata=[]
        self.dedmaca=[]
        #status flag
        self.status=True
        
    def set_name(self, name):
        self.name = name
        
    def set_working_dir(self, name):
        self.wd = name
        if not os.path.isdir(self.wd):
            errMsg("Directory \'%s\' does not exist!\n\n" % self.wd)
            sys.exit(1)
 
    def set_table_name(self, table_name):
        self.table_name = table_name
        #fn = self.wd+r'/'+table_name
        #if not os.access(fn, os.R_OK):
            #errMsg("File \'%s\' is not readable!\n\n" % fn)
            #sys.exit(1)
    def set_write_table_name(self, table_name):
        self.write_table_name = table_name.replace(' ', '_')
        fn = self.wd
        if not os.access(fn, os.W_OK):
            errMsg("Directory \'%s\' is not writable!\n\n" % fn)
            sys.exit(1)
            
    def update_consumption(self):
        self.np=self.table.dy
        self.tl=self.table.extract_column(TIME_COL)
        self.cl=self.table.extract_column(VALUE_COL)
        self.cda=self.table.extract_dictionary(TIME_COL, VALUE_COL)
        self.ta=numpy.array(self.tl)
        self.ca=numpy.array(self.cl)
            
    def read_table(self):
        try:
            fn=self.wd+r'/'+self.table_name
            if  os.stat(fn).st_size==0:
                errMsg('File  %s has size 0\n\n' %  fn)
                sys.exit(1)
            else:
                f=open(fn, 'r')
                list=f.readlines()
                f.close()
                list=remove_CR_LF_form_list(list)
        except IOError:
            errMsg('Cannot open for read %s' %  fn)
        self.status=True
        self.table=float_table(list, self.name, 2)
        self.update_consumption()
        if messaging.debug:
            self.table.print_table()
        
    def convert2float(self, vec):
        vector=[]
        for i, el in enumerate(vec):
            try:
                float_val=float(el)
                vector.append(float_val)
            except:
                errMsg("Entry %d of vector is not of type float: '%s'" % (i,  el))
                self.status=False
        return(vector)
        
    def check_strictly_increasing_new_row(self, vec):
        if self.status  != False:
            last_row=self.table.last_row()
            for j, el in enumerate(vec):
                if isinstance(el, float) and isinstance(last_row[j], float)  and self.table.strictly_increasing_check_mask[j]:
                    if last_row[j] >= el:
                        errMsg( "Entry [%d] of vector is not strictly increasing: '%s'" % ( j,   el))
                        self.status=False
        else:
            warnMsg("Method not executed due to previous errors!\n")
            
    def check_measurement_input(self, vec):
        if self.status  != False:
            last_row=self.table.last_row()
            first_row=self.table.first_row()
            #bisheriger Durchschnittsverbrauch pro Tag
            slope=(last_row[1]-first_row[1])/(last_row[0]-first_row[0])
            for j, el in enumerate(vec):
                #print j, el
                if isinstance(el, float) and isinstance(last_row[j], float)  and self.table.strictly_increasing_check_mask[j]:
                    if last_row[j] >= el:
                        if j == 0:
                            print '\nWrong input: Actual timestamp \'%.3f\' is smaller than latest table entry \'%.3f\'\n' % (el,  last_row[j])
                        if j == 1:
                            print '\nWrong input: Actual measurement \'%.3f\' is smaller than latest table entry \'%.3f\'\n' % (el,  last_row[j])
                        return False
                    else:
                        if j==1:
                            actual_slope=(el-last_row[j])/(vec[0]-last_row[0])
                            print '\nActual \'%s\' per day: \'%.3f\'\n' % (self.name, actual_slope)
                            if actual_slope > MAX_MEASUREMENT_VARIATION*slope:
                                print '\nWrong input: Actual measurement slope \'%.3f\' is more than \'x%s\' bigger than average slope \'%.3f\'\n' % (actual_slope,  MAX_MEASUREMENT_VARIATION,  slope)
                                return False   
            return True
        else:
            return False
    
    def add_row(self, row):
        if self.status != False:
            frow=self.convert2float(row)
            self.check_strictly_increasing_new_row(frow)
            if len(frow) != self.table.dx:
                errMsg("Dimension do not match:\nRequired: %d Actual: %d\n" % ( self.table.dx, len(frow)))
                self.status=False
            if self.status:
                self.table.add_row(frow)
                self.update_consumption()
                if messaging.debug:
                    self.table.print_table()
        else:
            warnMsg("Method not executed due to previous errors!\n")
            
    def add_column(self, column, strictly_increasing_flag):
        if self.status != False:
            fcolumn=self.convert2float(column)
            if len(fcolumn) != self.table.dy:
                errMsg("Dimension do not match:\nRequired: %d Actual: %d\n" % ( self.table.dy, len(fcolumn)))
                self.status=False
            if self.status:
                self.table.add_column(fcolumn, strictly_increasing_flag)
                self.update_consumption()
                if messaging.debug:
                    self.table.print_table()
        else:
            warnMsg("Method not executed due to previous errors!\n")
        
    def write_table(self):
        if self.status != False:
            try:
                fn=self.wd+r'/'+self.write_table_name
                f=open(fn, 'w')
                for row in self.table.list:
                    f.writelines(row +'\n')
                f.close()
            except IOError:
                errMsg('Cannot open for write %s' %  fn)
        else:
            warnMsg("Method not executed due to previous errors!\n")
            
    def xmgrace_time_to_AD_time (self, xmgrace_time_table):
        #please notice the offset of one of matplotlib.dates !
        #see e.g. http://matplotlib.org/api/dates_api.html
        offset_1970=datetime.datetime(1970, 1, 1, 1, 0, 0)-datetime.datetime(1, 1, 1, 1, 0, 0)
        AD_time_table=xmgrace_time_table+offset_1970.days+1
        return AD_time_table
        
    def linear_regression(self):
        """calculates liner regression of self.ta versus self.ca"""
        slope, intercept, r_value, p_value, std_err = stats.linregress(self.ta, self.ca)
        #print slope, intercept, r_value, p_value, std_err
        yi=slope*self.ta+intercept
        return yi
        
    def interpolate_at_equidistant_time_steps(self):
        #determine min and max of time series
        min_t=numpy.min(self.ta)/RESAMPLE_TIME_STEP
        max_t=numpy.max(self.ta)/RESAMPLE_TIME_STEP
        # mapping to quantization steps RESAMPLE_TIME_STEP
        min_ti=numpy.trunc(min_t)*RESAMPLE_TIME_STEP
        max_ti=numpy.trunc(max_t)*RESAMPLE_TIME_STEP
        number_of_samples=numpy.rint((max_ti-min_ti)/RESAMPLE_TIME_STEP+1+EPSILON)
        #print number_of_samples
        self.edta=numpy.linspace(min_ti, max_ti, number_of_samples)
        #print self.edta
        #scipy.interpolate.splrep: Find the B-spline representation of 1-D curve.
        rep = scipy.interpolate.splrep(self.ta,self.ca, k=1)
        self.edca=interpolate.splev(self.edta,rep)
        #print len(self.edta)
        #print number_of_samples
     
    def moving_average(self,  window_size,  scale,  title, xlabel, ylabel):
        if window_size < len(self.edta):
            j=0
            i=window_size
            imax=len(self.edta)
            self.edmata=numpy.copy(self.edta[window_size:])
            self.edmaca=[]
            while i < imax:
                #print i, j
                self.edmaca.append((self.edca[i]-self.edca[j])*scale)
                i = i + 1
                j = j + 1
            #print len(self.edmata)
            #print len(self.edmaca)
            graphics.my_2D_plot_of_arrays(self.edmata,  self.edmaca,  title, xlabel,  ylabel)
            
    def delta_moving_average(self, scale, title, xlabel, ylabel):
        if len(self.edmata) > 1:
            i=0
            j=1
            imax=len(self.edmata)
            self.dedmata=numpy.copy(self.edmata[1:])
            self.dedmaca=[]
            while j < imax:
                #print imax, i, j
                self.dedmaca.append((self.edmaca[j]-self.edmaca[i])*scale)
                i = i + 1
                j = j + 1
            #print len(self.dedmata)
            #print len(self.dedmaca)
            graphics.my_2D_plot_of_arrays(self.dedmata,  self.dedmaca,  title, xlabel,  ylabel)
            
    def input_measurement(self, consistency_check_on):
        if self.status != False:
            if self.table.dx != 2:
                errMsg("Dimension do not match:\nRequired: %d Actual: %d\n" % ( self.table.dx, '2'))
                self.status=False
        if self.status != False:
            # determine local time for the local timezone
            tl      = datetime.datetime.now()
            t1     = datetime.datetime(1970, 01, 01, 0, 0, 0)   # 1970-01-01 00:0:0
            tnow=(time.mktime(tl.timetuple())-time.mktime(t1.timetuple()))/24/3600
            done = False
            while not done:
                fp=input_float('Please input actual measurement of \'%s\'\n\n' % self.name)
                done = self.check_measurement_input([tnow, fp])
            self.add_row( [tnow, fp])
        else:
            warnMsg("Input of measurement value abandoned due to previous errors!\n")

    def consumption_analysis(self,  name,  working_dir,  input_file,  ylabel,
            consistency_check_on, input_flag):
        self.set_name(name)
        self.set_working_dir(working_dir)
        self.set_table_name(input_file)
        self.read_table()
        self.table.consistency_checks_on=consistency_check_on
        if input_flag:
            self.input_measurement(consistency_check_on)
        #self.add_row( [4.01,'6.999'])
        #self.add_column([ '6.001', '6.000', '6.0021',  6.003], STRICTLY_INCREASING)
        self.set_write_table_name(name + ".caf")
        self.write_table()
        self.ta= self.xmgrace_time_to_AD_time(self.ta)
        #linear regression
        yi=self.linear_regression()
        #plot of consumption over time and linear regression
        graphics.my_2D_plot_of_arrays(self.ta,  self.ca,  name,  'time [year]',  ylabel, self.ta,  yi,  'y-')
        #difference with numpy.diff
        cad=numpy.diff(self.ca, n=1)
        tad=numpy.diff(self.ta, n=1)
        avg_a=cad/tad
        #my_2D_plot_of_arrays(self.ta[1:],  avg_a,  'average of '+name,  'time [year]',  ylabel)
        self.interpolate_at_equidistant_time_steps()
        self.moving_average(1, 1/RESAMPLE_TIME_STEP, 'average of '+name,  'time [year]',  ylabel)
        self.moving_average(MOVING_AVERAGE_DAYS/RESAMPLE_TIME_STEP, 1, '365 days moving average of '+name,  'time [year]',  ylabel)
        self.delta_moving_average(1/RESAMPLE_TIME_STEP, 'delta of 1 year moving average of '+name,  'time [year]',  ylabel)

         
class float_table(object):
    """
    
    """
    
    def __init__(self,  list, name, dim):
        """                 """
        self.name=name
        self.status=True
        self.list = list
        self.array=[]
        self.split()
        self.dim=dim
        self.dx=0
        self.dy=0
        self.status=True
        self.consistency_checks_on=True
        self.strictly_increasing_check_mask=[1 for i in range(dim)]
        self.consistency_checks()
        
    def set_strictly_increasing_check_mask(self,  bitposition):
        self.strictly_increasing_check_mask[bitposition]=1
    
    def reset_strictly_increasing_check_mask(self,  bitposition):
        self.strictly_increasing_check_mask[bitposition]=0
            
    def consistency_checks(self):
        if self.consistency_checks_on:
            self.check_dimension()
            self.check_float()
            self.check_strictly_increasing()
            if not self.status:
                errMsg("Exiting because of previous fatal errors\n")
                sys.exit(1)
            else:
                self.dy=len(self.array)
                self.dx=len(self.array[0])
            
    def enable_consistency_checks(self):
        self.consistency_checks_on=True
       
    def disable_consistency_checks(self):
        self.consistency_checks_on=False
        
    def split(self):
        for entry in self.list:
            entry = entry.rstrip("\r\n")
            el = entry.strip() .split()
            self.array.append(el)
    
    def check_dimension(self):
        if self.status == True:
            i=0
            for entry in self.array:
                if len(entry) != self.dim:
                    errMsg("Line %d of table '%s' has not exactly %d entries: '%s'" % (i,  self.name,  self.dim,  entry))
                    self.status=False
                i+=1
            if len(self.strictly_increasing_check_mask) != self.dim:
                errMsg("strictly_increasing_check_mask of table '%s' has not exactly %d entries" % ( self.name,  self.dim))
                self.status=False
        else:
            warnMsg("Method not executed due to previous errors!\n")
            
   
    def check_float(self):
        if self.status == True:
            i=0
            for i, row in enumerate(self.array):
                for j, col in enumerate(row):
                    try:
                        val=float(col)
                        self.array[i][j]=val
                    except:
                        errMsg("Entry [%d][%d] of table '%s' is not of type float: '%s'" % (i, j,  self.name,  col))
                        self.status=False
        else:
            warnMsg("Method not executed due to previous errors!\n")
   
    def check_strictly_increasing(self):
        if self.status == True:
            for i, row in enumerate(self.array):
                if i>0:
                    for j, col in enumerate(row):
                        if  j <= len(prev)-1 and isinstance(col, float) and isinstance(prev[j], float)  and self.strictly_increasing_check_mask[j]:
                            if not col > prev[j]:
                                errMsg("Entry [%d][%d] of table '%s' is not strictly increasing: '%s'" % (i, j,  self.name,  col))
                                self.status=False
                prev=row
        else:
            warnMsg("Method not executed due to previous errors!\n")
        
    def extract_column(self, colnum):
        col=[]
        if colnum <= self.dx and colnum >= 0:
            for row in self.array:
                col.append(row[colnum])
        return col
    
    
    def extract_dictionary(self, colnum1,  colnum2):
        my_dict={}
        if colnum1 <= self.dx and colnum1 >= 0:
            if colnum2 <= self.dx and colnum2 >= 0:
                for row in self.array:
                    my_dict[row[colnum1]]=row[colnum2]
        return my_dict
        
    def add_column(self, newcol, strictly_increasing_flag):
        nextcol=self.dx
        if len(newcol) == self.dy:
            self.dx=nextcol+1
            for j, row in enumerate(self.array):
                row.append(newcol[j])
            for i, row in enumerate(self.list):
                self.list[i] = row + " " + str(newcol[i])
            self.dim+=1
            self.strictly_increasing_check_mask.append(strictly_increasing_flag)
            self.consistency_checks()
        else:
            warnMsg("Table: %s: Attempt to add column vector of wrong size!" % self.name)
            self.status=False
            
    def add_row(self, newrow):
        nextrow=self.dy
        if len(newrow) == self.dx:
            self.dy=nextrow+1
            self.array.append(newrow)
            addstr=''
            for el in newrow:
                addstr+=' '  + str(el)
            addstr=addstr.lstrip()
            self.list.append(addstr)
            self.consistency_checks()
        else:
            warnMsg("Table: %s: Attempt to add row vector of wrong size!" % self.name)
            self.status=False
            
    def last_row(self):
        return self.array[-1]
        
    def first_row(self):
        return self.array[0]
            
    def print_table(self):
        print '\nArray:\n'
        print self.array
        print '\nList:\n'
        print self.list
        


    
def main():
    
    import optparse
    parser = optparse.OptionParser(description=desc,  
        version='%prog version ' + __my_version__)
    
#    parser.add_option("-v", "--version",
#        dest="version",
#        default=False,
#        action="store_true",
#        help="print program versions and exit")
    
    parser.add_option('--nc', help='no consistency check',
        dest='no_consistency_check', action='store_true')
        
    parser.add_option('-i', help='input measurement(s)', 
        dest='input_flag', action='store_true')

    parser.add_option("--wdir", type="string",
        help="working directory", metavar="DIRECTORY", dest="wdir")
        
    parser.add_option("-v", help="show version", dest="version", 
        action='store_true')
                  
    parser.add_option("-e", help="analyze electrical power consumption",
        dest="epower", action='store_true')
        
    parser.add_option("--ef", type="string",
        help="file storing data base for electrical power consumption analysis", 
        metavar="FILE",dest="file_epower")   
    
    parser.add_option("-o", help="analyze oil consumption", dest="oil", 
        action='store_true')
        
    parser.add_option("--of", type="string", 
        help="file storing data base for oil consumption analysis", 
        metavar="FILE",dest="file_oil")   
    
    parser.add_option("-w", help="analyze water consumption", dest="water", 
        action='store_true')
        
    parser.add_option("--wf", type="string",
        help="file storing data base for water consumption analysis", 
        metavar="FILE",dest="file_water")   
    
    parser.set_defaults(verbose=0,  no_consistency_check=False,
        wdir=WORKING_DIR, epower=False, 
        file_epower=ELECTRICAL_POWER_CONSUMPTION_FILE, oil=False, 
        file_oil=OIL_CONSUMPTION_FILE, water=False,
        file_water=WATER_CONSUMPTION_FILE,  version=False, input_flag=False)
    
    (options, args) = parser.parse_args()
    
    if options.version:
        parser.print_version()
    else:
        stdMsg("\n\nconsal.py version %s\n" % __my_version__)
    
    #check if working directory is existing and writable
    check_working_directory(options.wdir)
    
    #analyze electrical power consumption
    if options.epower:
        stdMsg("\n\nStarting analysis of electrical power consumption ..\n")
        #check if data base file is existing and readable
        #check_database_file(options.wdir,  options.file_epower)
        #initialize data analysis
        power_supply=consumption()
        #run analysis
        power_supply.consumption_analysis('electrical power consumption',
            options.wdir, options.file_epower,  'electrical power [kWh]', 
            not(options.no_consistency_check), options.input_flag)
        
        
    
    #analyze oil consumption
    if options.oil:
        stdMsg("\n\nStarting analysis of oil consumption ..\n")
        #check if data base file is existing and readable
        check_database_file(options.wdir,  options.file_oil)
        #initialize data analysis
        oil=consumption()
        #run analysis
        oil.consumption_analysis('oil consumption', options.wdir, 
            options.file_oil,  'burning time of oil heating[h]', 
            not(options.no_consistency_check), options.input_flag)
    
    
    #analyze water consumption2
    if options.water:
        stdMsg("\n\nStarting analysis of water consumption ..\n")
         #check if data base file is existing and readable
        check_database_file(options.wdir,  options.file_water)
        #initialize data analysis
        water=consumption()
        #run analysis
        water.consumption_analysis('water consumption', options.wdir,
            options.file_water,  'fresh water [m^3]', not(options.no_consistency_check),          options.input_flag)
        
    if not options.epower and not options.oil and not options.water:
        stdMsg("\n\nNo analysis has been selected!")
 
    stdMsg("\nFinished\n")
    
if __name__ == '__main__':
    main()
