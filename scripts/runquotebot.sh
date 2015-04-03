#!/bin/bash
# Add this script to the server as crontab:
# $ crontab -e
# Then add the line:
# @reboot <path to optbot repo>/scripts/runquotebot.sh

optbot_home="/home/marshallfarrier/Workspace/optbot"
goodexits=(0)
env_cmd='source /mnt/disk1/venv/optbot/bin/activate'
srv_cmd='python '$optbot_home'/service/quotes.py --start'
secs_if_no_mongo=60
secs_to_retry=120

while [ true ]
do
    mongo_pid=`pidof mongod`
    if [ $mongo_pid ]
    then
        $env_cmd
        $srv_cmd
        exitcode=$?
        
        for code in ${goodexits[@]}
        do
            if [ $exitcode -eq $code ]
            then
                exit 0
            fi
        done
        sleep $secs_to_retry
    else
        sleep $secs_if_no_mongo
    fi
done
