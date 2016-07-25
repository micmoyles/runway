#!/usr/bin/python

import base_app
x = base_app.loader('/mnt/data/REMIT/','localhost')
x.whitelist = ['FREQ','SOSO']
x.username = 'root'
x.passwd = 'wiarreft'
x.cleanup = False
x.timeout = 0.2
x.__start__()
