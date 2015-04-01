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

import _constants
from _logger import logger
import conn

def pull(client):
    # abort if file already exists
    _fname = 'test.csv'
    if os.path.isfile(_fname):
        _msg = "File '{}' already exists. Remove file before writing".format(_fname)
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
    with open(_fname, 'w') as _csvfile:
        _writer = csv.DictWriter(_csvfile, fieldnames=_constants.FIELDNAMES) 
        _writer.writeheader()
        for _row in _cursor:
            _writer.writerow({_field: _row[_field] for _field in _constants.FIELDNAMES})

if __name__ == '__main__':
    _parser = argparse.ArgumentParser()
    _parser.add_argument('--pull', help='pull data from mongo to generate csv', action='store_true')
    _args = _parser.parse_args()
    if _args.pull:
        conn.job(pull, logger)
