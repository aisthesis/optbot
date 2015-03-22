"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Unobserve equity (:mod:`optbot.db.unobserve`)
=========================================

.. currentmodule:: optbot.db.unobserve

Remove equities passed from command line from `active` collection in mongodb.

Examples
--------
To remove 'ge' and 'f' from `active` collection:

    python3 unobserve.py ge f
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

import conn

def insert(equities, client):
    _db = client[_constants.DB]
    _active = _db[_constants.ACTIVE]
    _bulk = _active.initialize_unordered_bulk_op()
    _values = [{'equity': _eq} for _eq in equities]
    _alreadydone = True
    for _val in _values:
        if _active.find_one(_val) is None:
            logger.info("{} not present in {}.{}".format(_val, _constants.DB, _constants.ACTIVE))
        else:
            _alreadydone = False
            _bulk.find(_val).remove()
            logger.info("{} queued for removal from {}.{}".format(_val, _constants.DB, _constants.ACTIVE))
    if not _alreadydone:
        try:
            _result = _bulk.execute()
        except BulkWriteError:
            logger.exception("Error writing to database")
        else:
            logger.info("{} records removed from {}.{}".format(_result['nRemoved'], _constants.DB, _constants.ACTIVE))
    else:
        logger.info("none of given values found")

if __name__ == '__main__':
    conn.job(partial(insert, sys.argv[1:]), logger)
