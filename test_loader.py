#!/usr/bin/python

import base_app
x = base_app.loader('/mnt/data/REMIT','localhost')
x.whitelist = ['FREQ','SOSO']
x.username = 'root'
x.passwd = 'wiarreft'
x.cleanup = True 
x.timeout = 0.2
x.status = False
x.sql = 'mysql'
x.__start__()
