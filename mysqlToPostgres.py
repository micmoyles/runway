#!/usr/bin/python

import MySQLdb as mdb


def get_known_Assets():
    query = '''
   select name, AssetID, FuelType, NormalCapacity from plants
'''
    db = mdb.connect( self.db, self.username, self.passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use config' )
    cursor.execute( query )
    rows = cursor.fetchall()
    for row in rows:
        print row
    cursor.close()

get_known_Assets()