#!/usr/bin/python 

import datetime
import MySQLdb as mdb
from base_app import EApp
import plant
host = 'localhost'
user = 'erova'
passwd = 'er0va123'

# class to create productionProfiles for each plant found in the REMIT databases

class plantMonitor(EApp):

  def __init__( self ):

    super( plantMonitor, self).__init__()

    self.interval = []
    self.plants = []
    self.plant_list = []
    self.total = plant.plant('TOTAL',0.0)
    self.monitorLength   = 3.0  # days into the future
    self.monitorInterval = 60   # interval to monitor (minutes)
    self.query = '''
        select messageCreationTs as ts,NormalCapacity,AvailableCapacity from outages 
        where EventStart < '%s' 
        and EventEnd > '%s' 
        and AssetId = '%s' 
        order by ts desc 
        limit 1 
'''

  def runAssertions( self ):

    assert len(self.plants) > 0, 'Need to specify at least one plant'
    assert self.monitorLength is not None
    assert self.monitorInterval is not None


  def getIntervals( self ):

    maxMins = int(self.monitorLength * 24 * 60)
    self.intervals = range(0, maxMins + self.monitorInterval, self.monitorInterval) 


  def get_all_known_plants( self ):

    query = '''
    select distinct(AssetId), NormalCapacity from outages
'''
    # this query should be done from the plants table but currently it is incomplete
    db = mdb.connect( host, user, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use REMIT' )
    cursor.execute( query )
    rows = cursor.fetchall() 
    for row in rows: 
      name = row['AssetId']
      norm = row['NormalCapacity']
      self.plants.append(name)
      self.plant_list.append(plant.plant(name,norm))
    cursor.close()

  def check_status( self, time, plant ):
    time_for_query = datetime.datetime.now().strftime('%Y-%m-%d %H-%M')
    time_for_query = (datetime.datetime.now() + datetime.timedelta(minutes=time)).strftime( '%Y-%m-%d %H:%M')
    query = self.query % ( str(time_for_query), str(time_for_query), plant.name) 
    db = mdb.connect( host, user, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use REMIT' )
    cursor.execute( query )
    row = cursor.fetchone() # fetching one here is fine as we are only expecting one result
    cursor.close()

    if row is not None:
      return time_for_query, row['AvailableCapacity']
    else: return time_for_query, plant.NormalCapacity 
  
  def updateProductionProfiles( self ):

    db = mdb.connect( host, user, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use REMIT' )
    for plant in self.plant_list:
      for ts, cap in plant.productionProfile:
        command = '''
insert into productionProfiles(AssetID,timestamp,AvailableCapacity) values ('%s','%s',%d) 
''' % ( plant.name, ts, cap)   
        cursor.execute( command )
    db.commit()
    cursor.close()

  
  def start( self ):

    self.runAssertions()
    self.getIntervals()
    for interval in self.intervals:
      total_capacity = 0
      for plant in self.plant_list:
      #for interval in self.intervals:
        t, capacity = self.check_status(  interval, plant )
        total_capacity+=capacity
        plant.productionProfile.append(( t, capacity))
      self.total.productionProfile.append(( t, total_capacity))
    self.plant_list.append(self.total)
    for plant in self.plant_list: plant.writeJson('/var/www/hanger/plant_data')
    


p = plantMonitor()
p.get_all_known_plants()
p.start()
p.updateProductionProfiles()
