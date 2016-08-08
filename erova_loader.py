#!/usr/bin/python

import base_app
x = base_app.loader('/data/REMIT','localhost')
x.whitelist = ['FREQ','SOSO']
x.username = 'erova'
x.passwd = 'er0va123'
x.cleanup = True 
x.timeout = 0.2
x.status = False
x.sql = 'mysql'
x.__start__()
