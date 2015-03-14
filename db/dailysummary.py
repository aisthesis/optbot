"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT
"""

import pynance as pn

def summarize():
    _eq = 'spwr'
    _lowstrike = 28.
    _highstrike = 39.
    _exp1 = '2015-06-19'
    _exp2 = '2015-09-18'
    _cost = 9065.04
    _ncontracts = 50
    _nshares = _ncontracts * 100.
    _opts = pn.opt.get(_eq)
    _dblcal = _opts.spread.diag.dblcal(_lowstrike, _highstrike, _exp1, _exp2)
    _dblcal.loc['Cost', 'Value'] = _cost
    _dblcal.loc['CostPerShare', 'Value'] = _cost / _nshares
    _dblcal.loc['CurrValue', 'Value'] = _currval = _dblcal.loc['Debit', 'Value'] * _nshares
    _dblcal.loc['Profit', 'Value'] = _profit = _currval - _cost
    _dblcal.loc['ProfitPerShare', 'Value'] = _profit / _nshares
    _dblcal.loc['ProfitPct', 'Value'] = _profit / _cost
    return _dblcal

