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
import logging
logger = logging.getLogger('optbot')
handler = logging.FileHandler('/var/log/optbot/python.log')
_fmt = '%(asctime)s %(levelname)s %(module)s.%(funcName)s :  %(message)s'
formatter = logging.Formatter(_fmt)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

from functools import partial

import sys

import _constants
import conn

def insert(equities, client):
    _db = client[_constants.DB]
    _active = _db[_constants.ACTIVE]
    _values = [{'equity': _eq} for _eq in equities]
    for _val in _values:
        if _active.find_one(_val) is None:
            logger.info("{} not present in db {}.{}".format(_val, _constants.DB, _constants.ACTIVE))
        else:
            _active.delete_many(_val)
            logger.info("{} removed from db {}.{}".format(_val, _constants.DB, _constants.ACTIVE))

if __name__ == '__main__':
    conn.job(partial(insert, sys.argv[1:]), logger)
