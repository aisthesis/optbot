"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Constants (:mod:`optbot.db._constants`)
=======================================

.. currentmodule:: optbot.db._constants

Constants
"""
# logging
LOGNAME = 'optbot'
LOGFILE = '/var/log/optbot/python.log'
LOGFMT = '%(asctime)s %(levelname)s %(module)s.%(funcName)s :  %(message)s'

# database
DB = 'options'
# collections
ACTIVE = 'active'
QUOTES = 'quotes'

# retries for update
NRETRIES = 16
RETRYSECSTOSLEEP = 10 * 60

# timestamps in local time
TODAYSCLOSE = 13
