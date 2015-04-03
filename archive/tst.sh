#!/bin/bash
echo $(pidof mongod)
echo `pidof mongod`
mongopid=`pidof foo`
if [ $mongopid ]
then
    echo 'yes it is'
else
    echo 'no it is not'
fi
