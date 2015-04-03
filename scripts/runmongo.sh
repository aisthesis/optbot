#!/bin/bash
# Add this script to the server as crontab:
# $ sudo crontab -u mongodb -e
# Then add the line:
# @reboot <path to optbot repo>/scripts/runmongo.sh

#From http://docs.mongodb.org/manual/reference/exit-codes/
#130 is ctrl-c
GOODEXITS=(0 12 49 130)
CMD="mongod --config /etc/mongod.conf"

while [ true ]
do
    $CMD
    EXITCODE=$?
    
    for CODE in ${GOODEXITS[@]}
    do
        if [ $EXITCODE -eq $CODE ]
        then
            exit 0
        fi
    done
done
