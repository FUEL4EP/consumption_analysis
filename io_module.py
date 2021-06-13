#io_module.py
# -*- coding: utf-8 -*-

# $Rev: 63 $:  
# $Author: ewald $:  
# $Date: 2017-04-16 14:50:18 +0200 (So, 16. Apr 2017) $:
# $Id: io_module.py 63 2017-04-16 12:50:18Z ewald $ 

__version__ = "$Revision: 63 $"

import os
from messaging import  dbgMsg, errMsg,  warnMsg
import sys
import re

def isWritable(directory):
    try:
        tmp_prefix = "tmp_file_for_write_testing";
        count = 0
        filename = os.path.join(directory, tmp_prefix)
        while(os.path.exists(filename)):
            filename = "{}.{}".format(os.path.join(directory, tmp_prefix),count)
            count = count + 1
        f = open(filename,"w")
        f.close()
        os.remove(filename)
        return True
    except Exception as e:
        dbgMsg("specified working directory \'%s\' is not writable!\n" % directory)
        return False


def check_working_directory (directory):
    dbgMsg("checking working directory %s" % directory)
    if not os.path.exists(directory):
        errMsg("Specified working directory \'%s\' does not exist!\n\nPlease create the data base with the command line option '-n'\n" % directory)
        sys.exit(1)
    if not os.path.isdir(directory):
        errMsg("Specified working directory \'%s\' is not a directory!\n" % directory)
        sys.exit(1)
    if not isWritable(directory):
        errMsg("Specified working directory \'%s\' is not writable!\n" % directory)
        sys.exit()
    return True
    
def check_database_file (directory, file_name,  newDB):      
    fn = directory+r'/'+ file_name
    if newDB:
        print ("\nTrying to create a new data base: '%s'\n"  %  fn)
        if not os.path.isfile(fn):
            #create the specified data base file with size 0
            with open(fn, "w") as f:
                f.write("")
            print ("\n\nCreated a new data base file: '%s'\n" % fn)
        else:
            errMsg("Specified data base file \'%s\' does already exist!\n\nCannot create a data base with the same name as an existing one!\n\nAborting!\n\n" % fn)
            sys.exit(1)
    else:
        if not os.path.isfile(fn):
            errMsg("Specified data base file \'%s\' does not exist!\n\nPlease create the data base with the command line option '-n'\n" % fn)
            sys.exit(1)
    if not os.access(fn, os.R_OK):
        errMsg("Specified data base file \'%s\' is not readable!\n\n" % fn)
        sys.exit(1)
    if not newDB:
        if  os.stat(fn).st_size==0:
            warnMsg("Specified data base file \'%s\' has size of 0!\n\n" % fn)
    return True
    
def check_float(string):
    floatpattern=r'^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$'
    m=re.match(floatpattern, string)
    if m is not None:
       return True
    else:
        return False
    
def input_float(string):
    done=False
    while not done:
        myinput=input(string)
        done=check_float(myinput)
    fp=float(myinput)
    return fp
