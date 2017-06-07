#!/bin/bash
if [ $( pgrep -f mysql_loader ) ]
then
	echo 'process found....exiting'
	exit 1
fi
/usr/bin/python $PWD/mysql_loader.py &> loader.log &
sleep 2.0

current_pid=$( /usr/bin/pgrep -f mysql_loader )
echo 'launched with pid - ' $current_pid
/usr/bin/pgrep -f mysql_loader > loader.pid

if [ -f loader.monit ]
then 
	cp -f loader.monit /data/monit/loader.monit 	
else 
	echo 'monit config not found, process will not be monitored....'
fi
