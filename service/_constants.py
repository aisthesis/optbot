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
LOGFMT = '%(asctime)s %(levelname)s %(module)s.%(funcName)s :  %(message)s'

# database
DB = 'options'
# collections
ACTIVE = 'active'
QUOTES = 'quotes'
FIELDNAMES = ('Quote_Time', 'Underlying', 'Expiry', 'Opt_Type', 'Strike', 'Opt_Symbol',\
        'Last', 'Bid', 'Ask', 'Vol', 'Open_Int',)
INTFIELDS = ('Vol', 'Open_Int',)
FLOATFIELDS = ('Strike', 'Last', 'Bid', 'Ask',)
DATEFIELDS = ('Quote_Time', 'Expiry',)
STRFIELDS = ('Underlying', 'Opt_Type', 'Opt_Symbol',)

# retry parameters
RETRYSECS = 10. * 60.

# service management
TOPIC = 'optbot'
KILLSIG = TOPIC + '.kill'
MSGSIZE = 64

# testing
TESTDATAFILE = 'test.csv'
TESTDB = 'optionstst'
