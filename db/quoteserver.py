"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Get options quotes (:mod:`optbot.db.quoteserver`)
=================================================

.. currentmodule:: optbot.db.quoteserver

Run as background thread (append '&' to command)

Examples
--------
    python quoteserver.py &
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
from pytz import timezone
import socket
import threading
import traceback

import pandas as pd
from pandas.tseries.offsets import BDay
from pymongo.errors import BulkWriteError
import pynance as pn

import conn

class Checker(object):
    def __init__(self):
        self._job = None
        self._secstoretry = _constants.RETRYSECS
        self._running = False

    def run(self):
        _now = dt.datetime.now(tz=timezone('US/Eastern'))
        if not ismktopen(_now):
            logger.info("Market not open today: {}".format(_now))
            self._secstoretry = _constants.SECSINDAY
        elif _now.hour < 16:
            logger.info("Today's closes unavailable at {}".format(_now))
            self._secstoretry = (16. - _now.hour) * 60. * 60.
        elif conn.job(partial(updateall, _now), logger):
            logger.info("Successful retrieval at {}".format(_now))
            self._secstoretry = _constants.SECSONSUCC
        else:
            logger.info("Retrieval failed at {}".format(_now))
            self._secstoretry = _constants.RETRYSECS
        if self._running:
            logger.info("Retrying in {:.1f} hours".format(self._secstoretry / (60. * 60.)))
            self._job = threading.Timer(self._secstoretry, self.run)
            self._job.start()

    def start(self):
        logger.info("starting")
        self._running = True
        self.run()

    def close(self):
        logger.info("stopping")
        self._running = False
        self._job.cancel()

def ismktopen(date):
    return date.day == ((date + BDay()) - BDay()).day

def updateeq(db, eq, nysenow):
    _quotes = db[_constants.QUOTES]
    _today = dt.datetime(nysenow.year, nysenow.month, nysenow.day, 11)
    if _quotes.find_one({'Underlying': {'$in': [eq.lower(), eq.upper()]}, 'Quote_Time': {'$gte': _today}}) is not None:
        logger.warn("{} quotes for '{}' already inserted.".format(_today.strftime('%Y-%m-%d'), eq)) 
        return
    logger.info("Downloading options quotes for '{}'".format(eq))
    try:
        _opts = pn.opt.get(eq)
        _entries = _opts.tolist()
        if len(_entries) == 0:
            logger.info("Empty list returned for '{}'".format(eq))
            return False
        _bulk = _quotes.initialize_unordered_bulk_op()
        logger.info("Inserting quotes for '{}' into '{}'".format(eq, _constants.QUOTES))
        for _entry in _entries:
            _bulk.insert(_entry)
            logger.info("{} queued for insert into {}.{}".format(_entry, _constants.DB, _constants.QUOTES))
        try:
            _result = _bulk.execute()
        except BulkWriteError:
            logger.exception("Error writing to database")
            return False
        else:
            logger.info("{} records inserted into {}.{}".format(_result['nInserted'], _constants.DB, _constants.QUOTES))
            return True
    except pd.io.data.RemoteDataError:
        logger.exception("exception retrieving quotes for '{}'".format(eq))
        return False
    except:
        logger.exception("unknown exception")
        return False

def updateall(nysenow, client):
    _db = client[_constants.DB]
    _active = _db[_constants.ACTIVE]
    _success = True
    for _eq in _active.find():
        _success = updateeq(_db, _eq['equity'], nysenow) and _success
    return _success

def server():
    _host = ''
    _backlog = 1
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sock.bind((_host, _locconst.PORT))
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
            _client.send('quote server closing'.encode())

if __name__ == '__main__':
    server()
