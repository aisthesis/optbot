"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Observe equity (:mod:`optbot.service._logger`)
=========================================

.. currentmodule:: optbot.service._logger
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
