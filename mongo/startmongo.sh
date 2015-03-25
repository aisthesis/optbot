#!/bin/bash
# Run as user 'mongodb':
# $ sudo -u mongodb ./startmongo.sh
mongod --fork --config /etc/mongod.conf
