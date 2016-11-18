#!/usr/bin/python

import MySQLdb as mdb
username = 'erova'
hostname = 'localhost'
passwd = 'er0va123'


def get_known_Assets():
    query = '''
   select name, AssetID, FuelType, NormalCapacity from plants
'''
    db = mdb.connect( hostname, username, passwd)
    cursor = db.cursor( mdb.cursors.DictCursor )
    cursor.execute( 'use config' )
    cursor.execute( query )
    rows = cursor.fetchall()
    for row in rows:
        print row
    cursor.close()

get_known_Assets()