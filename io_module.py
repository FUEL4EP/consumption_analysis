#io_module.py
# -*- coding: utf-8 -*-

# $Rev: 60 $:  
# $Author: ewald $:  
# $Date: 2017-03-14 17:24:37 +0100 (Di, 14. Mär 2017) $:
# $Id: io_module.py 60 2017-03-14 16:24:37Z ewald $ 

__version__ = "$Revision: 60 $"

import os
from messaging import  dbgMsg, errMsg
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
        errMsg("specified working directory \'%s\' does not exist!\n" % directory)
        sys.exit(1)
    if not os.path.isdir(directory):
        errMsg("specified working directory \'%s\' is not a directory!\n" % directory)
        sys.exit(1)
    if not isWritable(directory):
        errMsg("specified working directory \'%s\' is not writable!\n" % directory)
        sys.exit()
    return True
    
def check_database_file (directory, file_name):      
    fn = directory+r'/'+ file_name
    if not os.path.isfile(fn):
        errMsg("Specified data base file \'%s\' does not exist!\n\n" % fn)
        sys.exit(1)
    if not os.access(fn, os.R_OK):
        errMsg("Specified data base file \'%s\' is not readable!\n\n" % fn)
        sys.exit(1)
    if  os.stat(fn).st_size==0:
        errMsg("Specified data base file \'%s\' has size of 0!\n\n" % fn)
        sys.exit(1)
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
        input=raw_input(string)
        done=check_float(input)
    fp=float(input)
    return fp
