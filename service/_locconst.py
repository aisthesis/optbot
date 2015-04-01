"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Local constants (:mod:`optbot.db._locconst`)
============================================

.. currentmodule:: optbot.db._locconst

This file should constants that may vary depending on
local configurations. It should only be modified in branch
'master'. To ignore changes locally::
    git update-index --assume-unchanged service/_locconst.py

To resume tracking::
    git update-index --no-assume-unchanged service/_locconst.py
"""
# logging
LOGFILE = '/var/log/optbot/python.log'

# service management
PORT = 50000
