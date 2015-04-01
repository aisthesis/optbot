#!/bin/bash
# Run as user 'mongodb':
# $ sudo -u mongodb ./startmongo.sh
# To do this with no password for sudo, first do:
# $ sudo su
# You are then root and can start mongo as user `mongodb`
mongod --fork --config /etc/mongod.conf
