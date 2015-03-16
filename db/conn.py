"""
.. Copyright (c) 2015 Marshall Farrier
   license http://opensource.org/licenses/MIT

Connection to MongoDB (:mod:`optbot.db.conn`)
===================================================

.. currentmodule:: optbot.db.conn

Opens and closes db connection.
"""
from pymongo import MongoClient

def job(fn, logger):
    _client = MongoClient()
    logger.info("db connection opened")
    fn(_client)
    _client.close()
    logger.info("db connection closed")
