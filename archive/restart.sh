#!/bin/bash
# Script must be run using sudo to mount disk
# to be run on startup
# mounts disk, starts mongo, starts server
mount /dev/sdb /mnt/disk1
pushd /home/marshallfarrier/Workspace/optbot/mongo
sudo -u mongodb ./startmongo.sh
popd
source /mnt/disk1/venv/optbot/bin/activate
pushd /home/marshallfarrier/Workspace/optbot/service
python quotes.py --start &
popd
