#!/usr/bin/python 

import datetime, log
import MySQLdb as mdb
from base_app import EApp
host = 'localhost'
user = 'erova'
passwd = 'er0va123'

# queries REMIT outage info for assetIDs and ensures they exist in config.plant and config.plant_status
def run_query( query ):
  db = mdb.connect( host, user, passwd)
  cursor = db.cursor( mdb.cursors.DictCursor )
  cursor.execute( query )
  rows = cursor.fetchall() 
  cursor.close()
  return rows

class plant_updater(EApp):
  def __init__( self ):
    EApp.__init__( self )
    self.query = '''
        select distinct(AssetId) ,NormalCapacity, FuelType from outages 
'''
    self.command = []
    self.currentCount = self.count_plants()

  def runAssertions( self ):
    assert len(self.plants) > 0, 'Need to specify at least one plant'
    assert self.monitorLength is not None
    assert self.monitorInterval is not None

  def count_plants( self ):
    query = ''' select count(distinct(AssetID)) as count from config.plants'''
    rows = run_query( query )
    count = rows[0]['count']
    return count

  def check_plants( self ):
    db = mdb.connect( host, user, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use REMIT' )
    cursor.execute( self.query )
    rows = cursor.fetchall() 
    for row in rows: 
      command = "insert ignore into plants(Name,AssetId,NormalCapacity,FuelType) values ('%s','%s',%d,'%s')" % (row['AssetId'],row['AssetId'], row['NormalCapacity'], row['FuelType'])
      #command = "insert ignore into plant_status(AssetId,Status,NormalCapacity,CurrentCapacity) values ('%s','%s',%d,'%s')" % (row['AssetId'],'OPEN', row['NormalCapacity'], row['NormalCapacity'])
      self.command.append(command)
    cursor.close()

  def insert_plants( self ):
    db = mdb.connect( host, user, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use config' )
    for command in self.command:
      cursor.execute( command )
    db.commit()  
    cursor.close()

  def start( self ):
    #self.runAssertions()
    #self.getIntervals()
    self.check_plants()
    if len(self.command) == self.currentCount:
      log.info('no new plants found, exiting')
    else:
      log.info('Found new plant, updating config.plants')
      self.insert_plants()
      log.info('Old count was %d, new count is %d' % (self.currentCount, self.count_plants()) )

p = plant_updater()
p.start()
