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
import _constants
import _locconst

import logging
logger = logging.getLogger(_constants.LOGNAME)
handler = logging.FileHandler(_locconst.LOGFILE)
formatter = logging.Formatter(_constants.LOGFMT)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

import datetime as dt
from functools import partial
import time

import pandas as pd
from pandas.tseries.offsets import BDay
import pymongo
from pymongo import MongoClient
import pynance as pn

import conn

def mktclose(date):
    return dt.datetime(date.year, date.month, date.day, _constants.TODAYSCLOSE)

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
        return True
    except pd.io.data.RemoteDataError as e:
        logger.error("exception retrieving quotes for '{}'".format(eq))
        logger.error(e)
        return False

def updateall(closingtime, tries, client):
    logger.info("Attempt {} of {}".format(tries + 1, _constants.NRETRIES))
    _db = client[_constants.DB]
    _active = _db[_constants.ACTIVE]
    _success = True
    for _eq in _active.find():
        _success = updateeq(_db, _eq['equity'], closingtime) and _success
    if tries  + 1 >= _constants.NRETRIES:
        return
    if not _success:
        # sleep, then try again
        time.sleep(_constants.RETRYSECSTOSLEEP)
        updateall(closingtime, tries + 1, client)

_now = dt.datetime.utcnow()
_todaysclose = mktclose(_now)
if not ismktopen(_todaysclose):
    logger.info("Market closed today. No update")
    exit(0)
if _now.hour < _constants.TODAYSCLOSE:
    logger.info("Closes unavailable at hour {}. No update".format(_now.hour))
    exit(0)
conn.job(partial(updateall, _todaysclose, 0), logger)
