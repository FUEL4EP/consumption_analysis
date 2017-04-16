# consumption_analysis
=======================

Python statistic software for consumption analysis of electrical power, fresh water, and oil

Installation:
=============

Put all python source code files of the reposotory into a working directory

<working_dir>/consal.py
             /graphics.py
             /io_module.py
             /messaging.py

Optional: Put example data bases into the working directory


<working_dir>/electrical_power_consumption.caf
             /oil_consumption.caf
             /water_consumption.caf
             
Required python modules:

sys, os, numpy, scipy, time, datetime, pylab, matplotlib, re, string, exceptions


Statistical analyses:
=====================

a)  average consumption per day (in command line)
b)  time chart of consumption with linear regression (matplotlib chart)
c)  time chart of average consumption between sampling points  (matplotlib chart)
d)  time chart of 365 days moving average of consumption  (matplotlib chart)
e)  time chart of delta of 1 year moving average of consumption  (matplotlib chart)


Usage:
======


Usage: consal.py [options]

consal.py is doing a statistical analysis of electrical power,  water, and oil
consumptions

Options:
  --version         show program's version number and exit
  -h, --help        show this help message and exit
  --nc              no consistency check
  -n                create a new data base
  -i                input measurement(s)
  --wdir=DIRECTORY  working directory
  -v                show version
  -e                analyze electrical power consumption
  --ef=FILE         file storing data base for electrical power consumption
                    analysis
  -o                analyze oil consumption
  --of=FILE         file storing data base for oil consumption analysis
  -w                analyze water consumption
  --wf=FILE         file storing data base for water consumption analysis


Examples on usage:

# Please store the provided example data bases *.caf in your working directory

1. Run analysis on provided data base for electrical power consumption:

consal -e

2. Run analysis on provided data base for water consumption:

consal -w


3. Run analysis on provided data base for heating oil consumption:


consal -o

4. Add a new consumption value to an existing data base and then run an analysis of electrical power consumption:

consal -i -e

5. Add a new consumption value to an existing data base and then run an analysis of water consumption:

consal -i -w


6. Add a new consumption value to an existing data base and then run an analysis of heating oil consumption:


consal -i -o


# Before creating a new data base, please reneame the provided example data bases *.caf in your working directory

7. Create a new data base for electrical power consumption:

consal -i -n -e


7. Create a new data base for water consumption:

consal -i -n -w

7. Create a new data base for heating oil consumption:

consal -i -n -o


Enjoy and have fun!












                                                                                                                               
                                                                                                                               
                                                                                                                               
                                                                                                                               
                                                                                                                               
                                                                                                                               
                                                                 
