#!/usr/bin/python

import loader
x = loader.loader('/data/REMIT','localhost')
x.whitelist = ['FREQ','SOSO']
x.appName = 'LOADER'
x.username = 'erova'
x.passwd = 'er0va123'
x.cleanup = True 
x.timeout = 0.2
x.status = False
x.sendEmailForOutages = False
x.sql = 'mysql'
x.__start__()
