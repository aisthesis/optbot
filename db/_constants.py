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

# retry parameters
RETRYSECS = 10. * 60.

# service management
TOPIC = 'optbot'
KILLSIG = TOPIC + '.kill'
MSGSIZE = 64
