#!/usr/bin/python

# right now this loader is not working because the xml parser does not return repeated elements.

import runway.loader as loader
x = loader.loader('/data/REMIT','localhost')
x.whitelist = ['IMBALNGC']
x.username = 'erova'
x.hostname = 'localhost'
x.passwd = 'er0va123'
x.cleanup = True 
x.timeout = 0.2
x.status = False
x.sql = 'mysql'
x.loadtoDB = False
x.__start__( dryrun = False )
