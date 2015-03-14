"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Daily update (:mod:`optbod.dailyupdate`)
========================================

.. currentmodule:: optbot.dailyupdate

Run daily to to save options quotes.

After creating directory /var/log/mongodb with `user` permissions, 
start mongodb as daemon using:

    $ mongod --fork --logpath /var/log/mongodb/db.log

Stop db using (on Linux):

    $ mongod --shutdown
    
The `shutdown` option is for some reason unavailable on OSX,
so you have to do:

    mongo admin --eval "db.shutdownServer()"

The resulting message is suggestive of errors, but the shutdown
appears clean.
"""

from __future__ import print_function
import datetime as dt

import pandas as pd
from pandas.tseries.offsets import BDay
import pymongo
from pymongo import MongoClient
import pynance as pn

# database
DB = 'options'
# collections
ACTIVE = 'active'
QUOTES = 'quotes'

def mktclose(date):
    return dt.datetime(date.year, date.month, date.day, 16)

def ismktopen(date):
    return date.day == ((date + BDay()) - BDay()).day

def updateeq(db, eq, closingtime):
    _quotes = db[QUOTES]
    _today = dt.datetime(closingtime.year, closingtime.month, closingtime.day, 11)
    if _quotes.find_one({'Underlying': {'$in': [eq.lower(), eq.upper()]}, 'Quote_Time': {'$gte': _today}}) is not None:
        print("{} quotes for '{}' already inserted.".format(_today.strftime('%Y-%m-%d'), eq)) 
        return
    print("Downloading options quotes for '{}'".format(eq))
    try:
        _opts = pn.opt.get(eq)
        print("Inserting quotes for '{}' into '{}'".format(eq, QUOTES))
        _quotes.insert_many(_opts.tolist())
    except pd.io.data.RemoteDataError as e:
        print("exception retrieving quotes for '{}'".format(eq))
        print(e)

def updateall(client, closingtime):
    _db = client[DB]
    _active = _db[ACTIVE]
    for _eq in _active.find():
        updateeq(_db, _eq['equity'], closingtime)

def connection(fn, closingtime):
    _client = MongoClient()
    print("db connection opened")
    fn(_client, closingtime)
    _client.close()
    print("db connection closed")

if __name__ == "__main__":
    _now = dt.datetime.now()
    _todaysclose = mktclose(_now)
    if not ismktopen(_todaysclose):
        print("Market closed today. Aborting update.")
        exit(0)
    if _now.hour < 16:
        print("Today's closes not yet available. Aborting update.")
        exit(0)
    connection(updateall, _todaysclose)
