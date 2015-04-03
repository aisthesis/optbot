#!/bin/bash
# Add this script to the server as crontab:
# $ sudo crontab -u quotebot -e
# Then add the line:
# @reboot <path to optbot repo>/scripts/runquotebot.sh

optbot_home="/home/marshallfarrier/Workspace/optbot"
goodexits=(0)
cmd='python '$optbot_home'/service/quotes.py --start'
secs_to_sleep=600

while [ true ]
do
    mongo_pid=`pidof mongod`
    if [ $mongo_pid ]
    then
        $cmd
        exitcode=$?
        
        for code in ${goodexits[@]}
        do
            if [ $exitcode -eq $code ]
            then
                exit 0
            fi
        done
    else
        sleep $secs_to_sleep
    fi
done
