#!/bin/bash 

# script to check the status of the streaming port and restart the subscriber if a connection is not seen 

res=$( /bin/netstat -apn | /bin/grep 61613 )
if [ ${#res} -lt 1 ]
then 
	/home/mmoyles/runway/launch_subscriber.sh restart 
fi
