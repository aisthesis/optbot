#!/bin/bash

mongod --fork --config /etc/mongod.conf

MONGOPID=$(pidof mongod)

if (0 le $MONGOPID) then
    cmd
fi
