# -*- coding: utf-8 -*-

DESCRIPTION = """
    Script file amqpcon
    Author: Alexey Kolyanov, 2016
"""

import os
import datetime
import sys
sys.path.append('/home/mmoyles/stomp.py-4.1.8')
import yaml
import time
import stomp
import xml.etree.ElementTree
import log

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

def dump_xml(message):
    dump = '/mnt/data/REMIT/'
    assert os.path.exists(dump), 'Missing %s directory' % dump
    base = dump + str(datetime.datetime.now().strftime('%Y%m%d')) 
    dirlist = os.listdir(dump)
    if len(dirlist) == 0: 
        counter = '0001'
    else:
        lastFile = sorted(dirlist)[len(dirlist) - 1]
        c = lastFile.split('-')[1] # 003.xml
        counter = c.split('.')[0] # 003
        counter = int(counter)
        counter=counter+1
        counter = '%04d' % counter
    newFile = base + '-' + str(counter) + '.xml'
    handle = open(newFile,'wb')
    handle.write(message)
    handle.write("\n")
    handle.close()
    log.info( 'Wrote file %s' % str(newFile) )

class XmlDictConfig(dict):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself 
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a 
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


def get_config(cfgpath):
    config = {}
    if not os.path.exists(cfgpath):
        if not os.path.exists(os.path.join(CUR_DIR, cfgpath)):
            raise ValueError("Config file %s is not found!" % cfgpath)
        cfgpath = os.path.join(CUR_DIR, cfgpath)
    with open(cfgpath, 'r') as cfgf:
        config = yaml.load(cfgf.read())
    return config


class MyListener(stomp.ConnectionListener):

    def on_error(self, headers, message):
        print('   !!!!!! Received an error \n%s' % message)

    def on_message(self, headers, message):
        dump_xml(message)
        #data = xml.etree.ElementTree.XML(message) 
	#xmldict = XmlDictConfig(data)
	#print xmldict
	#for node in data.iter(): print node.tag
       	#print('   ****** Received a message \n%s %s' % (str(datetime.datetime.now()) , message))


def main():
    config = get_config('settings.yaml')

    conn = stomp.Connection(host_and_ports=[(config['connection']['host'], config['connection']['port'])],
                            use_ssl=config['connection']['ssl'])
    conn.set_listener('', MyListener())
    conn.start()
    conn_headers = {
        'host': config['connection']['vhost'],
        'client-id': config['connection']['client_id'],
    }
    conn.connect(username=config['connection']['login'],
                 passcode=config['connection']['passcode'],
                 headers=conn_headers,
                 wait=True)

    log.info("connected")

    conn.subscribe(destination=config['subscription']['topic'],
                   id=config['subscription']['subscriptionid'],
                   ack=config['subscription']['ack'])
    log.info("subscribed")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        pass

    conn.disconnect()

    return 0


if __name__ == "__main__":
    retval = main()
    sys.exit(retval)
