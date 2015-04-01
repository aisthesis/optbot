"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Observe equity (:mod:`optbot.service.testdata`)
=========================================

.. currentmodule:: optbot.service.testdata

Generate test data.
"""
import argparse
from functools import partial
import sys

from pymongo.errors import BulkWriteError

import _constants
from _logger import logger
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

def remove(equities, client):
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
    _parser = argparse.ArgumentParser()
    _parser.add_argument('--pull', help='pull data from mongo to generate csv', action='store_true')
    _args = _parser.parse_args()
    if _args.pull:
        print('pulling')
    else:
        print('not pulling')
    logger.info('logs working')
