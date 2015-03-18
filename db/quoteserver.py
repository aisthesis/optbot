"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Get options quotes (:mod:`optbot.db.quoteserver`)
=================================================

.. currentmodule:: optbot.db.quoteserver

Run as background thread (append '&' to command)

Examples
--------
    python3 quoteserver.py &
"""
import _constants
import logging
logger = logging.getLogger(_constants.LOGNAME)
handler = logging.FileHandler(_constants.LOGFILE)
formatter = logging.Formatter(_constants.LOGFMT)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

import datetime as dt
from functools import partial
import socket
import threading
from threading import Thread
import time

import pandas as pd
from pandas.tseries.offsets import BDay
import pymongo
from pymongo import MongoClient
import pynance as pn

import conn

class QuoteChecker(Thread):
    def __init__(self):
        super().__init__()
        self._running = False

    def run(self):
        self._running = True
        while self._running:
            logger.info("Running")
            time.sleep(10)
        logger.info("closing quote checker")

    def close(self):
        self._running = False

class Checker(object):
    def __init__(self):
        self._job = None

    def run(self):
        logger.info("running")
        self._job = threading.Timer(2., self.run)
        self._job.start()

    def start(self):
        logger.info("starting")
        self.run()

    def close(self):
        logger.info("stopping")
        self._job.cancel()


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

def job():
    _now = dt.datetime.utcnow()
    _todaysclose = mktclose(_now)
    if not ismktopen(_todaysclose):
        logger.info("Market closed today. No update")
        exit(0)
    if _now.hour < _constants.TODAYSCLOSE:
        logger.info("Closes unavailable at hour {}. No update".format(_now.hour))
        #exit(0)
    conn.job(partial(updateall, _todaysclose, 0), logger)

def server():
    _host = ''
    _backlog = 1
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sock.bind((_host, _constants.PORT))
    _sock.listen(_backlog)
    _running = True
    _checker = Checker()
    _checker.start()
    while _running:
        _client, _address = _sock.accept()
        _msg = _client.recv(_constants.MSGSIZE).decode()
        if _msg == _constants.KILLSIG:
            _sock.shutdown(socket.SHUT_RDWR)
            _sock.close()
            _checker.close()
            _running = False
            _client.send('quote server closed'.encode())

if __name__ == '__main__':
    server()
