"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Get options quotes (:mod:`optbot.db.quotes`)
=================================================

.. currentmodule:: optbot.db.quotes

When started in default mode (without '--alwaysrun' option),
the script::
1.  checks whether it is a market day. 
    *   If not, it sets the timer to run the script again at 4:15 PM on the
        next business day.
    *   If so, it checks to see if the market is closed yet (after 4:00 PM).
        If the market is not yet closed, it sets the timer to try again at
        close.
2.  if it is a business day and after 4:00 PM EST, the checker attempts to retrieve
    quotes for options on all stocks contained in the 'active' collection
    of the database.
3.  if retrieval succeeds for all active equities, the connection is closed,
    and the timer is reset to try at 4:15 PM EST on the next business day.

    if retrieval fails, the server will keep retrying every 10 minutes
    up to midnight EST.

Notes
-----
Should normally run as background thread (append '&' to command). Cf. example
below for syntax.

Examples
--------
To start service normally::
    python quotes.py --start &

To stop service::
    python quotes.py --stop
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

import argparse
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

run_any_day = False

class Checker(object):
    def __init__(self):
        self._job = None
        self._secstoretry = _constants.RETRYSECS
        self._running = False
        # for more accurate logging of shutdown
        self._jobinprogress = False

    def run(self):
        self._jobinprogress = True
        _now = dt.datetime.now(tz=timezone('US/Eastern'))
        _mktday = ismktopen(_now)
        if not _mktday and not run_any_day:
            logger.info("Market not open today: {}".format(_now))
            self._secstoretry = _secstowait(_now)
        elif _now.hour < 16 and _mktday:
            logger.info("Today's closes unavailable at {}".format(_now))
            self._secstoretry = _secstowait(_now, True)
        elif conn.job(partial(updateall, _now), logger):
            logger.info("Successful retrieval at {}".format(_now))
            self._secstoretry = _secstowait(_now)
        else:
            logger.info("Retrieval failed at {}".format(_now))
            self._secstoretry = _constants.RETRYSECS
        if self._running:
            logger.info("Retrying in {:.1f} hours".format(self._secstoretry / (60. * 60.)))
            self._job = threading.Timer(self._secstoretry, self.run)
            self._job.start()
        else:
            # this should be the case when job is cancelled while in progress
            logger.info("checker stopped after task completed")
        self._jobinprogress = False

    def start(self):
        logger.info("starting")
        self._running = True
        self.run()

    def close(self):
        logger.info("stopping")
        self._running = False
        self._job.cancel()
        if not self._jobinprogress:
            logger.info("checker stopped, next run canceled")


def ismktopen(date):
    return date.day == ((date + BDay()) - BDay()).day

def _secstowait(curr_est, againtoday=False):
    if againtoday:
        if curr_est.hour < 16:
            _nextclose = curr_est.replace(hour=16, minute=15)
            return (_nextclose - curr_est).total_seconds()
        return _constants.RETRYSECS
    _nextbday = curr_est + BDay()
    _nextclose = _nextbday.replace(hour=16, minute=15)
    return (_nextclose - curr_est).total_seconds()

def updateeq(db, eq, nysenow):
    _quotes = db[_constants.QUOTES]
    # PyMongo mistakenly interprets the value of 'Quote_Time' as UTC rather than EST
    # So we need to offset by at least 5 hours.
    # The following checks for any stored value from today regardless of quote time.
    _today = nysenow.replace(hour=3)
    if _quotes.find_one({'Underlying': {'$in': [eq.lower(), eq.upper()]}, 'Quote_Time': {'$gte': _today}}) is not None:
        logger.warn("{} quotes for '{}' already inserted.".format(nysenow.strftime('%Y-%m-%d'), eq)) 
        return True
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
            logger.debug("{} queued for insert into {}.{}".format(_entry, _constants.DB, _constants.QUOTES))
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

def startservice():
    _host = '127.0.0.1'
    _backlog = 1
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _sock.bind((_host, _locconst.PORT))
    _sock.listen(_backlog)
    _running = True
    _checker = Checker()
    _checker.start()
    while _running:
        _client, _address = _sock.accept()
        _msg = _client.recv(_constants.MSGSIZE).decode()
        if _msg == _constants.KILLSIG:
            _checker.close()
            _running = False
            _client.send('quote server closing'.encode())
    _client.close()

def stopservice():
    _host = 'localhost'
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sock.connect((_host, _locconst.PORT))
    _sock.send(_constants.KILLSIG.encode())
    _response = _sock.recv(_constants.MSGSIZE).decode()
    _sock.close()
    logger.info(_response)
    print(_response)

if __name__ == '__main__':
    _parser = argparse.ArgumentParser()
    _parser.add_argument("--start", help="start quote service", action="store_true")
    _parser.add_argument("--stop", help="stop quote service", action="store_true")
    _parser.add_argument("-A", "--alwaysrun", help="insert quotes on weekends and holidays",
            action="store_true")
    _args = _parser.parse_args()
    if _args.stop:
        stopservice()
    elif _args.start:
        run_any_day = _args.alwaysrun
        if _args.alwaysrun:
            logger.info("Inserting quotes even on weekends and holidays")
        startservice()
    else:
        _parser.print_help()
