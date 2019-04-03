#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/6/16 17:54
@File    : redis.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
from redis import StrictRedis, ConnectionPool


_redis_client_dic = {}


def get_channel(*args):
    """
    'md.{market}.{period}.{symbol}' or 'md.{period}.{symbol}'
    例如：
    md.huobi.Min1.ethusdt
    md.huobi.Tick.eosusdt
    通过 redis-cli 可以 PUBSUB CHANNELS 查阅活跃的频道
    :param market:
    :param period:
    :param symbol:
    :return:
    """
    if len(args) == 0:
        channel_str = 'md'
    else:
        channel_str = 'md.' + '.'.join(args)
    return channel_str


def get_redis(host, port, db=0) -> StrictRedis:
    """
    get StrictRedis object
    :param host:
    :param port:
    :param db:
    :return:
    """
    if db in _redis_client_dic:
        redis_client = _redis_client_dic[db]
    else:
        conn = ConnectionPool(host=host, port=port, db=db)
        redis_client = StrictRedis(connection_pool=conn)
        _redis_client_dic[db] = redis_client
    return redis_client
