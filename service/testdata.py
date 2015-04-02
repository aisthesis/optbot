"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Observe equity (:mod:`optbot.service.testdata`)
=========================================

.. currentmodule:: optbot.service.testdata

Generate test data.
"""
import argparse
import csv
import datetime as dt
import os.path
import sys

from pymongo.errors import BulkWriteError

import _constants
from _logger import logger
import conn

def pull(client):
    # abort if file already exists
    if os.path.isfile(_constants.TESTDATAFILE):
        _msg = "File '{}' already exists. Remove file before writing".format(_constants.TESTDATAFILE)
        print(_msg)
        logger.warn(_msg)
        return
    # get sample values from db
    _db = client[_constants.DB]
    _coll = _db[_constants.QUOTES]
    _eq = 'spwr'
    _type = 'call'
    _strike = 31
    _expiry = dt.datetime(2015, 6, 19)
    _qry = {'Underlying': {'$in': [_eq.lower(), _eq.upper()]}, 'Strike': _strike,\
            'Opt_Type': _type, 'Expiry': _expiry} 
    logger.info("Pulling test data")
    _cursor = _coll.find(_qry)
    # write to file
    with open(_constants.TESTDATAFILE, 'w') as _csvfile:
        _writer = csv.DictWriter(_csvfile, fieldnames=_constants.FIELDNAMES) 
        _writer.writeheader()
        for _row in _cursor:
            _writer.writerow({_field: _row[_field] for _field in _constants.FIELDNAMES})

def buildtstdb(client):
    logger.info("Retrieving test data from file")
    # abort if no file
    if not os.path.isfile(_constants.TESTDATAFILE):
        _msg = "File '{}' not found. No data to push to database".format(_constants.TESTDATAFILE)
        print(_msg)
        logger.warn(_msg)
        return
    # retrieve data to push
    _entries = []
    with open(_constants.TESTDATAFILE) as _csvfile:
        _reader = csv.DictReader(_csvfile)
        for _row in _reader:
            _entries.append(_typecast(_row))
    # push to test_db
    _db = client[_constants.TESTDB]
    _coll = _db[_constants.QUOTES]
    # abort if test db is already populated
    if _coll.find_one():
        _msg = "Collection {}.{} already populated. Insertion aborted".format(_constants.TESTDB, _constants.QUOTES)
        print(_msg)
        logger.warn(_msg)
        return
    logger.info("Inserting test data into {}.{}".format(_constants.TESTDB, _constants.QUOTES))
    _bulk = _coll.initialize_unordered_bulk_op()
    for _entry in _entries:
        _bulk.insert(_entry)
    try:
        _result = _bulk.execute()
    except BulkWriteError:
        _msg = "Error writing to {}.{}".format(_constants.TESTDB, _constants.QUOTES)
        logger.exception(_msg)
        print(_msg)
    else:
        _msg = "{} records inserted into {}.{}".format(_result['nInserted'], _constants.TESTDB, _constants.QUOTES)
        logger.info(_msg)
        print(_msg)

def _typecast(row):
    _ret = {}
    for _field in _constants.INTFIELDS:
        _ret[_field] = int(float(row[_field]))
    for _field in _constants.FLOATFIELDS:
        _ret[_field] = float(row[_field])
    for _field in _constants.DATEFIELDS:
        _ret[_field] = dt.datetime.strptime(row[_field], '%Y-%m-%d %H:%M:%S')
    for _field in _constants.STRFIELDS:
        _ret[_field] = row[_field]
    return _ret


if __name__ == '__main__':
    _parser = argparse.ArgumentParser()
    _parser.add_argument('--pull', help='pull data from mongo to generate csv', action='store_true')
    _args = _parser.parse_args()
    if _args.pull:
        conn.job(pull, logger)
    else:
        conn.job(buildtstdb, logger)
