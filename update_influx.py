#!usr/bin/python
import MySQLdb as mdb

from update_plantconfig import run_query
# query mysql and write data to influx using the http curl post
outputfile = '/home/erova/runway/influxdata.txt'
f = open(outputfile,'w')
query = '''
select unix_timestamp(pp.timestamp) as ts, pp.AssetID, pc.FuelType, pc.NormalCapacity, pp.AvailableCapacity  from REMIT.productionProfiles pp join config.plants pc on pc.AssetId = pp.AssetId where pp.timestamp > '2016-08-30 16:00:00' ; 
'''
res = run_query( query )
for r in res:
  cmd = 'productionProfiles,FuelType=%s,AssetID=%s value=%f %10d' % (r['FuelType'],r['AssetID'],float(r['AvailableCapacity']),r['ts'])
  f.write(cmd)
  f.write('\n')

f.close()
