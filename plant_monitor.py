#!/usr/bin/python 

import datetime
import MySQLdb as mdb
from base_app import EApp
host = 'localhost'
user = 'erova'
passwd = 'er0va123'

class plant:
# this class should really get the plants normal capacity from a DB query rather than needing it on initialisation
  def __init__( self , name, NormalCapacity ):
    self.name = name
    self.NormalCapacity = NormalCapacity
    self.productionProfile = []

class plant_monitor(EApp):
  def __init__( self ):
    EApp.__init__( self )
    self.interval = []
    self.plants = []
    self.plant_list = []
    self.monitorLength = 0.5 # days into the future
    self.monitorInterval = 60# interval to monitor (minutes)
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
    # this query should be done from the plats table but currently it is incomplete
    db = mdb.connect( host, user, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use REMIT' )
    cursor.execute( query )
    rows = cursor.fetchall() 
    for row in rows: 
      name = row['AssetId']
      norm = row['NormalCapacity']
      self.plants.append(name)
      self.plant_list.append(plant(name,norm))
    cursor.close()

  def check_status( self, time, plant ):
    time_for_query = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    time_for_query = (datetime.datetime.now() + datetime.timedelta(minutes=time)).strftime( '%Y-%m-%d %H:%M:%S')
    query = self.query % ( str(time_for_query), str(time_for_query), plant.name) 
    db = mdb.connect( host, user, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use REMIT' )
    cursor.execute( query )
    row = cursor.fetchone() # fetching one here is fine as we are only expecting one result
    cursor.close()
    if row is not None: 
      return row['AvailableCapacity']
    else: return plant.NormalCapacity 

  
  def start( self ):
    self.runAssertions()
    self.getIntervals()
    for plant in self.plant_list:
      for interval in self.intervals:
        capacity = self.check_status(  interval, plant )
        plant.productionProfile.append(( interval, capacity))
      plant.productionProfile = dict(plant.productionProfile)
      output = []
      for i in self.intervals:
        output.append(plant.productionProfile[i])
      print plant.name, output


p = plant_monitor()
p.get_all_known_plants()
p.start()
