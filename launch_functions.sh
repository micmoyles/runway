#!/bin/bash

# keep basic functions together so launch scripts look tidy

function check_for_running {
	script=$1	
	echo $script
	if [ $( pgrep -f $script ) ]
	then
        	echo 'process found....exiting'
        	exit 1
	fi
}
