#!/usr/bin/python 

import datetime
import MySQLdb as mdb
from base_app import EApp
host = 'localhost'
user = 'erova'
passwd = 'er0va123'

# queries REMIT outage info for assetIDs and ensures they exist in config.plant

class plant_updater(EApp):
  def __init__( self ):
    EApp.__init__( self )
    self.query = '''
        select distinct(AssetId) ,NormalCapacity, FuelType from outages 
'''
    self.command = []
  def runAssertions( self ):
    assert len(self.plants) > 0, 'Need to specify at least one plant'
    assert self.monitorLength is not None
    assert self.monitorInterval is not None


  def check_plants( self ):
    db = mdb.connect( host, user, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use REMIT' )
    cursor.execute( self.query )
    rows = cursor.fetchall() 
    for row in rows: 
      print row['AssetId'], row['NormalCapacity'], row['FuelType']
      command = "insert into plants(Name,AssetId,NormalCapacity,FuelType) values ('%s','%s',%d,'%s')" % (row['AssetId'],row['AssetId'], row['NormalCapacity'], row['FuelType'])
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
    print self.command
    self.insert_plants()

p = plant_updater()
p.start()
