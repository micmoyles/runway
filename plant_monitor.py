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
    self.query = '''
        select messageCreationTs as ts,EventStart,EventEnd,AssetID,EventType,NormalCapacity,AvailableCapacity from outages 
        where EventStart < '%s' 
        and EventEnd > '%s' 
        and AssetID = '%s' 
        order by ts desc 
        limit 1 
'''
  def check_status( self, time, plant ):
    time_for_query = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    query = self.query % ( str(time_for_query), str(time_for_query), plant) 
    print query
    db = mdb.connect( host, user, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use REMIT' )
    cursor.execute( query )
    row = cursor.fetchone() # fetching one here is fine as we are only expecting one result
    print plant, row['AvailableCapacity']
    cursor.close()
  
  def start( self ):
    for plant in self.plants:
      self.check_status( 0, plant )
p = plant_monitor()
p.plants = ['DRAXX-1','WBUPS-1']
p.start()
