"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT
"""
from __future__ import print_function

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
    _dblcal.loc['Put Strike', 'Value'] = _lowstrike
    _dblcal.loc['Call Strike', 'Value'] = _highstrike
    _dblcal.loc['Expiry 1', 'Value'] = _exp1
    _dblcal.loc['Expiry 2', 'Value'] = _exp2
    return _dblcal

if __name__ == '__main__':
    print(summarize())
