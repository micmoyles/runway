#!/bin/bash

PORT=61613

while true
do
	res=$( netstat -apn | grep $PORT )
	size=${#res}
        if [ $size == 0 ]
        then
           echo 'Exiting...'
           exit 0
        fi
        sleep 1
done
