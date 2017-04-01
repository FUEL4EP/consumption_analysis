#!/usr/bin/env python

import csv

ofile=open('/home/ewald/budget.csv',  "wb")

writer =csv.writer(ofile, quoting=csv.QUOTE_NONE)

off0=4
delta_p=8
delta_d=17

for j in range (10):
    for i in range(20):
        row= "'''1. REL funded resources!A%d" % (off0+i*delta_p+j*(delta_d+19*delta_p))
        print row
        writer.writerow([row])
ofile.close()
