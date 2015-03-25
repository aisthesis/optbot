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

    python observe.py ge f
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

from functools import partial
import sys

from pymongo.errors import BulkWriteError

import conn

def insert(equities, client):
    _db = client[_constants.DB]
    _active = _db[_constants.ACTIVE]
    _bulk = _active.initialize_unordered_bulk_op()
    _values = [{'equity': _eq} for _eq in equities]
    _alreadydone = True
    for _val in _values:
        if _active.find_one(_val) is not None:
            logger.info("{} already present in {}.{}".format(_val, _constants.DB, _constants.ACTIVE))
        else:
            _alreadydone = False
            _bulk.insert(_val)
            logger.info("{} queued for insert into {}.{}".format(_val, _constants.DB, _constants.ACTIVE))
    if not _alreadydone:
        try:
            _result = _bulk.execute()
        except BulkWriteError:
            logger.exception("Error writing to database")
        else:
            logger.info("{} records inserted into {}.{}".format(_result['nInserted'], _constants.DB, _constants.ACTIVE))
    else:
        logger.info("all values already present")


if __name__ == '__main__':
    conn.job(partial(insert, sys.argv[1:]), logger)
