"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Observe equity (:mod:`optbot.db.observe`)
=========================================

.. currentmodule:: optbot.db.observe

Add equities passed from command line to `active` collection in mongodb.

Examples
--------
To add 'ge' and 'f' to `active` collection:

    python3 observe.py ge f
"""
import logging
logger = logging.getLogger('optbot')
handler = logging.FileHandler('/var/log/optbot/python.log')
_fmt = '%(asctime)s %(levelname)s %(module)s.%(funcName)s :  %(message)s'
formatter = logging.Formatter(_fmt)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

import sys

import _constants
import connection

def mktclose(date):
    return dt.datetime(date.year, date.month, date.day, 16)

def ismktopen(date):
    return date.day == ((date + BDay()) - BDay()).day

def updateeq(db, eq, closingtime):
    _quotes = db[QUOTES]
    _today = dt.datetime(closingtime.year, closingtime.month, closingtime.day, 11)
    if _quotes.find_one({'Underlying': {'$in': [eq.lower(), eq.upper()]}, 'Quote_Time': {'$gte': _today}}) is not None:
        logger.warn("{} quotes for '{}' already inserted.".format(_today.strftime('%Y-%m-%d'), eq)) 
        return
    logger.info("Downloading options quotes for '{}'".format(eq))
    try:
        _opts = pn.opt.get(eq)
        logger.info("Inserting quotes for '{}' into '{}'".format(eq, QUOTES))
        _quotes.insert_many(_opts.tolist())
    except pd.io.data.RemoteDataError as e:
        logger.error("exception retrieving quotes for '{}'".format(eq))
        logger.error(e)

def updateall(client, closingtime):
    _db = client[DB]
    _active = _db[ACTIVE]
    for _eq in _active.find():
        updateeq(_db, _eq['equity'], closingtime)

def connection(fn, closingtime):
    _client = MongoClient()
    logger.info("db connection opened")
    fn(_client, closingtime)
    _client.close()
    logger.info("db connection closed")

if __name__ == '__main__':
    equities = sys.argv[1:]
    pass
