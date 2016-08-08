#!/usr/bin/python 

import datetime
import MySQLdb as mdb
from base_app import EApp
host = 'localhost'
user = 'erova'
passwd = 'er0va123'

class plant_monitor(EApp):
  def __init__( self ):
    EApp.__init__( self )
    self.interval = []
    self.plants = []
    self.monitorLength = 5 # days into the future
    self.monitorInterval = 30# interval to monitor (minutes)
    self.query = '''
        select messageCreationTs as ts,NormalCapacity,AvailableCapacity from outages 
        where EventStart < '%s' 
        and EventEnd > '%s' 
        and AssetID = '%s' 
        order by ts desc 
        limit 1 
'''
  def runAssertions( self ):
    assert len(self.plants) > 0, 'Need to specify at least one plant'
    assert self.monitorLength is not None
    assert self.monitorInterval is not None

  def getIntervals( self ):
    maxMins = int(self.monitorLength * 24 * 60)
    intervals = range(0, maxMins + self.monitorInterval, self.monitorInterval) 
    print intervals

  def check_status( self, time, plant ):
    time_for_query = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    time_for_query = (datetime.datetime.now() + datetime.timedelta(minutes=time)).strftime( '%Y-%m-%d %H:%M:%S')
    query = self.query % ( str(time_for_query), str(time_for_query), plant) 
    db = mdb.connect( host, user, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use REMIT' )
    cursor.execute( query )
    row = cursor.fetchone() # fetching one here is fine as we are only expecting one result
    if row is not None: print plant, time, row['AvailableCapacity']
    cursor.close()
  
  def start( self ):
    self.runAssertions()
    self.getIntervals()
    for plant in self.plants:
      self.check_status(  30, plant )
      self.check_status(  60, plant )
      self.check_status(  90, plant )
      self.check_status( 120, plant )

p = plant_monitor()
p.plants = ['DRAXX-1','T_CNQPS-3']
p.start()