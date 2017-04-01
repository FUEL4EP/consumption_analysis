#!/usr/bin/env python

import csv

ofile=open('/home/ewald/budget.csv',  "wb")

writer =csv.writer(ofile, quoting=csv.QUOTE_NONE)

off0=4
delta_p=8
delta_d=17
non_PLS_list=["wafer", "JIG", "NRE", "software", "consulting"]

for j in range (10):
    for i in range(20):
        for k in range(5):
            row= "'''1. REL funded resources!A%d" % (off0+i*delta_p+j*(delta_d+19*delta_p))
            print row
            writer.writerow([row, non_PLS_list[k]])
for j in range (10):
    for i in range(20):
        for k in range(5):
            row= "'''2. REE funded resources!A%d" % (off0+i*delta_p+j*(delta_d+19*delta_p))
            print row
            writer.writerow([row, non_PLS_list[k]])
            
ofile.close()
