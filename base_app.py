#!usr/bin/python
import socket
import datetime as dt
import log,os
from elexon_push_data import XmlDictConfig
import xml.etree.ElementTree
from time import sleep
import MySQLdb as mdb
import smtplib
from email.mime.text import MIMEText
import psycopg2 as pdb
import utils



class EApp:

  def __init__( self ):

    self.launchtime = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    self.status = False

  def writeStatus( self ):

    statusPath = '/home/erova/runway/status/'
    writetime = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    assert os.path.exists( statusPath ),'Could not find status directory, not continuing'
    
    pass

class loader(EApp):
    # this needs to parse the XML file and upload it to the database
  def __init__(self,root_directory,database_host):

    EApp.__init__(self)
    self.root_directory = root_directory
    self.archive_directory = root_directory + '/archive/'
    self.transmit_directory = root_directory + '/transmit/'
    self.hostname = None
    self.sql = None
    self.username = None
    self.passwd = None
    self.cleanup = True
    self.timeout = 2.0
    self.blacklist = []
    self.whitelist = []
    self.isBlack = False
    self.isWhite = False
    self.knownAssets = []
    self.loadtoDB = True
    self.mailer = smtplib.SMTP('localhost')
    self.psql = False
    self.mysql = False
    self.sendEmailForOutages = False
    assert os.path.exists(self.root_directory),'Could not find root directory, not continuing'
    assert os.path.exists(self.archive_directory),'Could not find archive directory, not continuing'
    assert os.path.exists(self.transmit_directory),'Could not find transmit directory, not continuing'

  def findSql( self ):
    if self.sql in ['mysql']:
      self.mysql = True
    elif self.sql in ['postgres','psql']:
      self.psql = True

  def get_known_Assets( self ):

    query = '''
   select distinct(AssetId) from plants 
'''
    if self.mysql:

      db = mdb.connect( self.hostname, self.username, self.passwd )
      cursor = db.cursor( mdb.cursors.DictCursor )
      cursor.execute( 'use config' )
      cursor.execute( query )
      rows = cursor.fetchall()
      for row in rows:
        name = row['AssetId']
        self.knownAssets.append(name)
      cursor.close()

    elif self.psql:
 
      db = pdb.connect(" dbname='remit' user=%s host=%s password=%s" % (self.username, self.hostname, self.passwd))
      db.autocommit = True
      cursor = db.cursor()
      cursor.execute( query )
      rows = cursor.fetchall()
      for row in rows:
        name = row['AssetId']
        self.knownAssets.append(name)
      db.commit()
      cursor.close()

  def _parse(self,xmlfile):
    
    # method to parse the file and return a string to populate a DB table
    # in its current form the xmltodict method only returns a single dict entry
    # for multiple xml elements
    
    tree = xml.etree.ElementTree.parse(xmlfile)
    root = tree.getroot()
    msg = XmlDictConfig(root)
    log.info(msg)
    if 'flow' in msg.keys():
      # then we are handling a stream formatted message
      load_cmd = self.parseflow( msg )
    elif 'DocumentType' in msg.keys():
      # then we are handling a pull data message that been placed on the stream network
      if msg['DocumentType'] == 'REMIT_document':
        log.info( 'Loading REMIT doc')
        load_cmd = self.parseREMIT( msg )	
      
      
  
  def parseflow( self , msg ):

    msgType = msg['flow']
    if msgType not in self.whitelist: 
      return 0
    log.info('Loading flow message %s' % str(msgType))

    if msgType == 'IMBALNGC':
      log.info('IMBALNGC message')
      log.info(msg)
		
    elif msgType == 'FREQ':

      SF = msg['msg']['row']['SF']
      TS = msg['msg']['row']['TS'] 
      TS = TS.strip(':GMT')

      if self.mysql:
        load_cmd = 'insert ignore into frequency values ( " %s " , %f ) ' % (str(TS), float(SF) ) 
      elif self.psql:
        load_cmd = "insert into frequency( timestamp, freq ) values ( '%s' , %f ) " % (str(TS), float(SF) ) 

    elif msgType == 'SOSO':
      data = msg['msg']['row']
      pubTs = msg['pubTs'].strip(':GMT')
      PT = data['PT']
      TD = data['TD'] 
      IC = data['IC']
      ST = data['ST'].strip(':GMT')
      TT = data['TT']
      TQ = data['TQ']
      # create table SOSO ( pubTs timestamp, PT float(10,5) , TD varchar(3), IC varchar(30), ST timestamp, TT varchar(30), TQ int(100) ,unique(pubTs) );
      if self.mysql:
        load_cmd = 'insert ignore into SOSO values ( "%s" , %f,"%s", "%s" , "%s" , "%s", %d ) ' % (str(pubTs), float(PT), TD, IC, ST, TT, int(TQ) ) 
      elif self.psql:
        load_cmd = "insert into SOSO(pubTs,PT,TD,IC,ST,TT,TQ) values ( '%s' , %f,'%s', '%s' , '%s' , '%s', %d ) " % (str(pubTs), float(PT), TD, IC, ST, TT, int(TQ) ) 
    
    if self.loadtoDB: self.load_to_database( load_cmd )
    return 0   
     
  def parseREMIT( self, msg ):

    log.info('Loading REMIT message')
    creationTs = msg['CreatedDateTime']
    data = msg['InsideInformation']
    d = data
    eventType = data['EventType']

    try:

      ordered_data = [ creationTs, 
             d['AffectedUnitEIC'],
             d['AssetType'],
             d['AffectedUnit'],
             d['DurationUncertainty'],
             d['RelatedInformation'],
             d['AssetId'],
             d['EventType'],
             float(d['NormalCapacity']),
             float(d['AvailableCapacity']),
             d['EventStatus'],
             d['EventStart'],
             d['EventEnd'],
             d['Cause'],
             d['FuelType'],
             d['Participant_MarketParticipantID'],
             d['MessageHeading'].replace(' ','_') ]

    except KeyError:

      log.info('Key error in file')
      return 0

    if eventType == 'FAILURE':
      log.info('Failure message recieved, I should tell someone')

      body = str(ordered_data)
      log.info('Logging body')
      log.info(body)

      if d['EventStatus'] == 'OPEN' and self.sendEmailForOutages:

        try:
         utils.sendEmail( body )

#          msg = MIMEText( body )
#          msg['To'] = toAddress
#          msg['Cc'] = ccAddress
#          msg['Subject'] = "FAILURE"
#          self.mailer.sendmail( fromAddress, toAddress, msg.as_string() )

        except smtplib.SMTPException:
          log.info('Error, unable to send email....')

      if self.mysql:

        load_cmd = 'insert ignore into outages values ("%s","%s","%s","%s","%s","%s","%s","%s",%f,%f,"%s","%s","%s","%s","%s","%s","%s")' % tuple(ordered_data)

      elif self.psql:

        fields = ('messagecreationts','affecteduniteic','assettype','affectedunit','durationuncertainty',
                  'relatedinformation','assetid','eventtype','normalcapacity','availablecapacity','eventstatus',
                  'eventstart','eventend','cause','fueltype','participant_marketparticipantid','messageheading')
        load_cmd = '''
insert into outages(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) values (TIMESTAMP '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',TIMESTAMP '%s',TIMESTAMP '%s','%s','%s','%s','%s')
''' % ( fields + tuple(ordered_data)  )
#        load_cmd = '''
#insert into outages(messagecreationts,affecteduniteic,assettype,affectedunit,durationuncertainty,relatedinformation,assetid,eventtype,normalcapacity,availablecapacity,eventstatus,eventstart,eventend,cause,fueltype,participant_marketparticipantid,messageheading) values (TIMESTAMP '2017-11-19T14:55:09Z','48W00000DRAXX-2C','Production','DRAXX-2','None','Biomass','DRAXX-2','FAILURE',645.0,580.0,'CANCELLED',TIMESTAMP '2017-11-19T15:04:00Z',TIMESTAMP '2017-11-19T20:06:30Z','Boiler / Fuel Supply','OTHER','DRAXX','REMIT_INFORMATION')
#'''
        log.info(load_cmd)
		
      if self.loadtoDB: self.load_to_database( load_cmd )
    return 0 
    
  def load_to_database( self, load_cmd ):

    assert self.sql in ['mysql','psql','postgres'], 'sql attribute needs to be mysql or psql'

    log.info( load_cmd )

    if self.mysql:

      db_cmd = 'use REMIT'
      db = mdb.connect( self.hostname, self.username , self.passwd )
      cursor = db.cursor(mdb.cursors.DictCursor)
      cursor.execute( db_cmd )
      cursor.execute( load_cmd )
      db.commit()
      cursor.close()

    elif self.psql:

      db=pdb.connect(" dbname='remit' \
             user=%s \
             host=%s \
             password=%s" % (self.username , self.hostname , self.passwd ))
      db.autocommit = True
      cursor = db.cursor()
      try:
        cursor.execute( load_cmd )
        db.commit()
      except:
        log.error('Formatting error in following message, could not load')
        log.info( load_cmd )
      cursor.close()

    return 0

  def get_file(self):

    file_list = os.listdir(self.transmit_directory)
    if len(file_list) == 0: return None
    this_file = sorted(file_list)[0] #choose newest file
    this_file = self.transmit_directory + this_file
    log.info(this_file)

    # check file is not empty
    file_info = os.stat( this_file )
    if file_info.st_size == 0:
    # if it is, then delete the current file and call the method again
    # on the nested call, the next non-zero file should be selected and this if statement will not be entered... lets hope
      log.error( 'Removing %s - file is empty' % str(this_file) )
      os.remove( this_file )
      this_file = self.get_file() 

    return str(this_file)

  def load_and_clear( self ):

    current_file = self.get_file()
    if current_file is None: return None 
    self._parse( current_file )
    log.info( 'Archiving %s' % str( current_file ) ) 
    if self.cleanup: os.rename( current_file , current_file.replace('transmit','archive') )

    return 0
    
  def loadDirectory( self ):

    file_list = os.listdir( self.root_directory )

    for f in file_list:
      self._parse( str(self.root_directory) + '/' + f )
	

  def __start__(self):

    self.findSql()
    assert (self.username is not None) and (self.passwd is not None) and (self.hostname is not None), 'Loader needs username, password and host configured'
    assert self.sql in ['mysql','psql','postgres'], 'loader needs to know what kind of database language to use - mysql or postgres (psql)'
    assert (len(self.whitelist) * len(self.blacklist)) == 0 , "Cannot have a whitelist and a blacklist %d %d" % (len(self.whitelist), len(self.blacklist))
    assert (self.mysql != self.psql), 'Can only use one kind of database language, either both are True or both are False'

    if self.status: self.writeStatus()

    if len(self.whitelist) != 0:
      self.isWhite = True

    if len(self.blacklist) != 0:
      self.isBlack = True
    self.get_known_Assets()
    log.info( self.__dict__ )

    while True:

     ret_val = self.load_and_clear()

     if ret_val is None:

       log.info('No files found, snoozing for 30 seconds')
       sleep( 30 )

     else:

       sleep( self.timeout )



