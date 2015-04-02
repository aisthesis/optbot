"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Utility functions (:mod:`optbot.service.utils`)
=================================================

.. currentmodule:: optbot.service.utils
"""
import datetime as dt

from pandas.tseries.offsets import BDay
from pytz import timezone

def fixentry(nysenow, entry):
    _fixed = entry
    _quotetime = ((nysenow + BDay()) - BDay()).to_datetime().replace(hour=entry['Quote_Time'].hour, 
            minute=entry['Quote_Time'].minute, second=entry['Quote_Time'].second)
    _fixed['Quote_Time'] = _quotetime
    _fixed['Expiry'] = entry['Expiry'].replace(tzinfo=timezone('US/Eastern'))
    return _fixed 
