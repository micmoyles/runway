#!/usr/bin/python

import runway.loader as loader
x = loader.loader('/data/REMIT')
x.appName = 'LOADER'
x.whitelist = []
x.username = 'blank'
x.passwd = 'blank'
x.hostname = 'postgres.cfqfdoajjaoa.eu-west-1.rds.amazonaws.com'
x.cleanup = True 
x.timeout = 0.2
x.status = False
x.sql = 'psql'
x.sendEmailForOutages = False
x.__start__()
