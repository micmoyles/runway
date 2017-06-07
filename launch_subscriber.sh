#!/bin/bash

# parse args 
action=$1
path=/home/mmoyles/runway
if [ $action == 'restart' ]
then
	echo 'killing any known processes'
	known=$( /usr/bin/pgrep -f remitSubscriber)
	echo $known
	/usr/bin/pkill -f remitSubscriber 
fi

if [ $( pgrep -f remitSubscriber) ]
then
	echo 'process found...exiting'
        exit 1
fi
if [ -f $path/subscriber.log ]
then
	cat subscriber.log >> subscriber-archive.log
fi
/usr/bin/python $path/remitSubscriber.py &> $path/subscriber.log &
/usr/bin/pgrep -f remitSubscriber > $path/subscriber.pid

if [ -f $path/subscriber.monit ]
then 
	cp -f $path/subscriber.monit /data/monit/subscriber.monit
else 
	echo 'monit config not found, process will not be monitored....'
fi
