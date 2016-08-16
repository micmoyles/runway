#!/bin/bash 

# script to launch app, create PID file and redirect logging. 

cmd=$1
sourcefile=$2
app=$( echo $sourcefile | cut -d. -f1 )
echo $app
pidfile=$( echo $app.pid )
logfile=$( echo $app.log ) 
echo $pidfile
echo $logfile

basepath=/home/erova/runway

case $cmd in
  'start')
     res=$( pgrep -cf $sourcefile )
     echo res is $res, len is ${#res}
     if [ ${#res} -gt 1 ]; then echo "$app already running, exiting"; exit 0 ; fi
     ./$sourcefile &> $basepath/$logfile &
     PID=$( pgrep -f $sourcefile )
     echo $PID > $basepath/$pidfile
     ;;
  'stop')
    res=$( pgrep -f $sourcefile )
    if [ ${#res} == 0 ]; then echo "$app not running, exiting"; exit 0 ; fi
    echo $res
    echo "This will now kill $res process"
    kill $res
    ;;
esac    
