#!/usr/bin/python 

import urllib2
response = urllib2.urlopen('https://api.bmreports.com/BMRS/B1510/V1?StartDate=2016-07-24&EndDate=2016-07-27&StartTime=14:00:00%20ZZ&EndTime=14:00:00%20ZZ&ServiceType=xml&APIKey=jsp06qkyw8zr8uw')
info = response.info()
#  response.info()['Content-Disposition'] will contain attachment info
filename='OUTAGE_B1510_201607242037.xml' # or get using response.info()
data = response.read()
fh = open(filename,'w')
fh.write(data)
fh.close()
