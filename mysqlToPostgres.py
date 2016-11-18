#!/usr/bin/python

import MySQLdb as mdb
import psycopg2 as pdb
username = 'erova'
hostname = 'localhost'
passwd = 'er0va123'


query = '''
   select name, AssetID, FuelType, NormalCapacity from plants
'''
db = mdb.connect( hostname, username, passwd)
m_cursor = db.cursor( mdb.cursors.DictCursor )
m_cursor.execute( 'use config' )
m_cursor.execute( query )
rows = m_cursor.fetchall()

conn=pdb.connect("  dbname='config' \
                         user='erova' \
                         host='postgres.cfqfdoajjaoa.eu-west-1.rds.amazonaws.com' \
                         password='05LHTo0bMQc4kv'")

p_cursor = conn.cursor()
p_cmd = 'insert into plants (name, assetid, fueltype, normalcapacity) values( \'%s\', \'%s\', \'%s\', %d);'

for row in rows:
    print( p_cmd % (row['name'], row['AssetID'], row['FuelType'],row['NormalCapacity']) )
    p_cursor.execute( p_cmd % (row['name'], row['AssetID'], row['FuelType'],row['NormalCapacity']) )

conn.commit()
m_cursor.close()
p_cursor.close()

