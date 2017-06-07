#!/usr/bin/python 

import datetime
import MySQLdb as mdb
from base_app import EApp


class plant:
# this class should really get the plants normal capacity from a DB query rather than needing it on initialisation
  def __init__( self , name, NormalCapacity ):
    self.name = name
    self.NormalCapacity = NormalCapacity
    self.productionProfile = []
    self.status = 'OPEN'

  def writeJson( self, JsonPath):
    assert JsonPath is not None
    JsonFilename = JsonPath + '/' + str(self.name) + '.json'
    template = '[ ' 
    for ts, cap in self.productionProfile:
      text = '{ "timestamp": "%s" , "capacity" : %d },' % (ts, cap)
      template = template + text
    template = template + ']'
    template = template.replace('},]','}]')
    f = open(JsonFilename,'w')
    f.write(template)
    f.close()
