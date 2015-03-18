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
LOGFILE = '/mnt/my-data/log/optbot/python.log'
LOGFMT = '%(asctime)s %(levelname)s %(module)s.%(funcName)s :  %(message)s'

# database
DB = 'options'
# collections
ACTIVE = 'active'
QUOTES = 'quotes'

# retry parameters
RETRYSECS = 10. * 60.
SECSONSUCC = 16. * 60. * 60.
SECSINDAY = 24. * 60. * 60.

# service management
TOPIC = 'optbot'
KILLSIG = TOPIC + '.kill'
PORT = 50000
MSGSIZE = 64
