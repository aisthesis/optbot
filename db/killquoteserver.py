"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Get options quotes (:mod:`optbot.db.killquoteserver`)
=====================================================

.. currentmodule:: optbot.db.killquoteserver

Examples
--------
    python3 killquoteserver.py
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

import socket

def kill_service():
    _host = 'localhost'
    _sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _sock.connect((_host, _locconst.PORT))
    _sock.send(_constants.KILLSIG.encode())
    _response = _sock.recv(_constants.MSGSIZE).decode()
    _sock.close()
    logger.info(_response)
    print(_response)

if __name__ == '__main__':
    kill_service()
