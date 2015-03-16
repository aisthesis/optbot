#!/usr/bin/python3
"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Daily update (:mod:`optbot.db.dailyupdate`)
===========================================

.. currentmodule:: optbot.db.dailyupdate

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
import logging
logger = logging.getLogger('optbot')
handler = logging.FileHandler('/var/log/optbot/python.log')
_fmt = '%(asctime)s %(levelname)s %(module)s.%(funcName)s :  %(message)s'
formatter = logging.Formatter(_fmt)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

import datetime as dt
from functools import partial

import pandas as pd
from pandas.tseries.offsets import BDay
import pymongo
from pymongo import MongoClient
import pynance as pn

import _constants
import conn

def mktclose(date):
    return dt.datetime(date.year, date.month, date.day, 16)

def ismktopen(date):
    return date.day == ((date + BDay()) - BDay()).day

def updateeq(db, eq, closingtime):
    _quotes = db[_constants.QUOTES]
    _today = dt.datetime(closingtime.year, closingtime.month, closingtime.day, 11)
    if _quotes.find_one({'Underlying': {'$in': [eq.lower(), eq.upper()]}, 'Quote_Time': {'$gte': _today}}) is not None:
        logger.warn("{} quotes for '{}' already inserted.".format(_today.strftime('%Y-%m-%d'), eq)) 
        return
    logger.info("Downloading options quotes for '{}'".format(eq))
    try:
        _opts = pn.opt.get(eq)
        logger.info("Inserting quotes for '{}' into '{}'".format(eq, _constants.QUOTES))
        _quotes.insert_many(_opts.tolist())
    except pd.io.data.RemoteDataError as e:
        logger.error("exception retrieving quotes for '{}'".format(eq))
        logger.error(e)

def updateall(closingtime, client):
    _db = client[_constants.DB]
    _active = _db[_constants.ACTIVE]
    for _eq in _active.find():
        updateeq(_db, _eq['equity'], closingtime)

def connection(fn, closingtime):
    _client = MongoClient()
    logger.info("db connection opened")
    fn(_client, closingtime)
    _client.close()
    logger.info("db connection closed")

_now = dt.datetime.now()
_todaysclose = mktclose(_now)
if not ismktopen(_todaysclose):
    logger.info("Market closed today. No update")
    exit(0)
if _now.hour < 16:
    logger.info("Today's closes not yet available. No update")
    exit(0)
conn.job(partial(updateall, _todaysclose), logger)
