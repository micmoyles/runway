#!/usr/bin/python

import loader
x = loader.loader('/data/REMIT')
x.appName = 'LOADER'
x.whitelist = []
x.username = 'erova'
x.passwd = '05LHTo0bMQc4kv'
x.hostname = 'postgres.cfqfdoajjaoa.eu-west-1.rds.amazonaws.com'
x.cleanup = True 
x.timeout = 0.2
x.status = False
x.sql = 'psql'
x.sendEmailForOutages = False
x.__start__()
