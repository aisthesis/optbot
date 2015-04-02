#!/bin/bash
# Script must be run using sudo to unmount disk
# to be run before shutting down instance
# stops server, mongo, unmounts disk
source /mnt/disk1/venv/optbot/bin/activate
pushd /home/marshallfarrier/Workspace/optbot/service
python quotes.py --stop
popd
pushd /home/marshallfarrier/Workspace/optbot/mongo
./stopmongo.sh
popd
umount -d /dev/sdb
