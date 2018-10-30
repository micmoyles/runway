#!usr/bin/python
import datetime as dt
import log,os
import utils


class EApp( object ):

  def __init__( self ):

    self.launchtime = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    self.status = False
    self.appName = None

  def writeStatus( self ):

    assert self.appName is not None, 'appName required to write status'
    statusPath = '/tmp/status/'
    statusFile = statusPath + self.appName
    writetime = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    uptime = writetime - self.launchtime
    assert os.path.exists( statusPath ),'Could not find status directory, not continuing'
    
    pass

