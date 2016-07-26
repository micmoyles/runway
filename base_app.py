#!/usr/bin/python
import socket
import datetime as dt
import struct
import sys,log,os
from elexon_push_data import XmlDictConfig
import xml.etree.ElementTree
from time import sleep
import MySQLdb as mdb
import psycopg2 as pdb 

class EApp:
    def __init__( self ):
	self.launchtime = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.status = True

    def writeStatus( self ):
        statusPath = '/home/mmoyles/status/'
        assert os.path.exists( statusPath ),'Could not find status directory, not continuing'
        
        pass
class loader(EApp):
        # this needs to parse the XML file and upload it to the database
    def __init__(self,root_directory,database_host):
        EApp.__init__(self)
	self.root_directory = root_directory
        self.db = database_host
        self.sql = 'mysql'
        self.username = None
        self.passwd = None
        self.cleanup = True
        self.timeout = 2.0
        self.blacklist = []
        self.whitelist = []
        self.isBlack = False
        self.isWhite  = False
        assert os.path.exists(self.root_directory),'Could not find root directory, not continuing'
        
    def _parse(self,xmlfile):
        
        # method to parse the file and return a string to populate a DB table
        # in its current form the xmltodict method only returns a single dict entry
        # for multiple xml elements
        
        tree = xml.etree.ElementTree.parse(xmlfile)
        root = tree.getroot()
        msg = XmlDictConfig(root)
        log.info(msg)
        if 'flow' in msg.keys():
			load_cmd = self.parseflow( msg )
		elif 'DocumentType' in msg.keys():
			if msg['DocumentType'] == 'REMIT_document':
				load_cmd = self.parseREMIT( msg )	
            
            
    
    def parseflow( self , msg ):
		msgType = msg['flow']  
		
		if msgType not in self.whitelist: 
			return 0
		log.info('Loading flow message')
		
        if msgType == 'FREQ':
           SF = msg['msg']['row']['SF'] 
           TS = msg['msg']['row']['TS'] 
           TS = TS.strip(':GMT')
           if self.sql == 'mysql': 
              load_cmd = 'insert ignore into frequency values ( " %s " , %f ) ' % (str(TS), float(SF) ) 
           elif self.sql == 'psql':
              load_cmd = "insert into frequency( timestamp, freq )  values ( '%s' , %f ) " % (str(TS), float(SF) ) 

        elif msgType == 'SOSO':
           data = msg['msg']['row']
           pubTs = msg['pubTs'].strip(':GMT')
           PT = data['PT']
           TD = data['TD'] 
           IC = data['IC']
           ST = data['ST'].strip(':GMT')
           TT = data['TT']
           TQ = data['TQ']
           #  create table SOSO ( pubTs timestamp, PT float(10,5) , TD varchar(3), IC varchar(30), ST timestamp, TT varchar(30), TQ int(100) ,unique(pubTs) );
           if self.sql == 'mysql': 
              load_cmd = 'insert ignore into SOSO values ( "%s" , %f,"%s", "%s" , "%s" , "%s", %d ) ' % (str(pubTs), float(PT), TD, IC, ST, TT, int(TQ) ) 
           elif self.sql == 'psql':
              load_cmd = "insert into SOSO(pubTs,PT,TD,IC,ST,TT,TQ) values ( '%s' , %f,'%s', '%s' , '%s' , '%s', %d ) " % (str(pubTs), float(PT), TD, IC, ST, TT, int(TQ) ) 
        
        self.load_to_database( load_cmd )
        return 0      
         
	def parseREMIT( self, msg ):
		log.info('Loading REMIT message')
		data = msg['InsideInformation']
		eventType = data['EventType']
		if eventType == 'FAILURE':
			log.alert('Failure message recieved, I should tell someone')
		if self.sql == 'mysql':
		    load_cmd = 'insert ignore into outages values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' % tuple(data.values())
		elif self.sql == 'psql':
			load_cmd = 'insert into outages(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)' % ( tuple(data.keys() + data.values() ) )
		log.info(load_cmd)
		
		return load_cmd	
     

		
        
    def load_to_database( self, load_cmd ):
        assert self.sql in ['mysql','psql','postgres'], 'sql attribute needs to be mysql or psql' 
        log.info( load_cmd )
        if self.sql == 'mysql':	
           db_cmd = 'use REMIT'
           db = mdb.connect( self.db, self.username , self.passwd )
           cursor = db.cursor(mdb.cursors.DictCursor)
           cursor.execute( db_cmd )
           cursor.execute( load_cmd )
           db.commit()
           cursor.close()
	elif self.sql in ['psql','postgres']:
           db=pdb.connect("  dbname='erova' \
                         user='erova' \
                         host='postgres.cfqfdoajjaoa.eu-west-1.rds.amazonaws.com' \
                         password='05LHTo0bMQc4kv'")
           db.autocommit = True
           cursor = db.cursor()
           cursor.execute( load_cmd )
           db.commit()
           cursor.close()
        return 0

    def get_file(self):
        file_list = os.listdir(self.root_directory)
        if len(file_list) == 0: return None
        this_file = sorted(file_list)[0] #choose newest file
	log.info(this_file)
        return str(self.root_directory) + '/' + str(this_file)

    def load_and_clear( self ):
        current_file = self.get_file()
        if current_file is None: return 
        self._parse( current_file )
        log.info( 'Deleting %s' % str( current_file ) ) 
        os.remove( current_file )
       
    def loadDirectory( self ):
        file_list = os.listdir( self.root_directory )
        for f in file_list:
            self._parse( str(self.root_directory) + '/' + f )
	
    def __start__(self):

       assert (self.username is not None) and (self.passwd is not None) and (self.db is not None), 'Loader needs username, password and host configured'
       assert (len(self.whitelist)  * len(self.blacklist)) == 0 , "Cannot have a whitelist and a blacklist %d %d" % (len(self.whitelist), len(self.blacklist))
       if self.status: self.writeStatus()
       if len(self.whitelist) != 0:
          self.isWhite = True
       if len(self.blacklist) != 0:
          self.isBlack = True
       log.info( self.__dict__ )

       if self.cleanup: 
          while True:
             self.load_and_clear()
             sleep( self.timeout )
       else: 
          self.loadDirectory()
          log.info('Directory loaded. Exiting')
          sys.exit()



