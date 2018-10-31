#!/usr/bin/python

import runway.loader as runwayloader
x = runwayloader.loader('/data/REMIT')
x.whitelist = ['FREQ','SOSO']
x.appName = 'LOADER'
x.username = 'erova'
x.passwd = 'er0va123'
x.hostname = 'localhost'
x.cleanup = True 
x.timeout = 0.2
x.status = False
x.sendEmailForOutages = False
x.sql = 'mysql'
x.__start__(dryrun = True)
