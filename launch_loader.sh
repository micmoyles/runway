#!/bin/bash

/usr/bin/python /home/erova/runway/postgres_loader.py &> loader.log &
pgrep -u erova -f postgres_loader > loader.monit


