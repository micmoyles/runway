#!/usr/bin/python

import base_app
x = base_app.loader('/data/REMIT','localhost')
x.whitelist = []
x.username = 'erova'
x.passwd = '05LHTo0bMQc4kv'
x.hostname = 'postgres.cfqfdoajjaoa.eu-west-1.rds.amazonaws.com'
x.cleanup = False
x.timeout = 0.2
x.status = False
x.sql = 'psql'
x.__start__()
