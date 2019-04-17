#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 19-4-3 下午5:28
@File    : __init__.py.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import logging
from logging.config import dictConfig

# log settings
logging_config = dict(
    version=1,
    formatters={
        'simple': {
            'format': '%(asctime)s %(name)s|%(module)s.%(funcName)s:%(lineno)d %(levelname)s %(message)s'}
    },
    handlers={
        'file_handler':
            {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logger.log',
                'maxBytes': 1024 * 1024 * 10,
                'backupCount': 5,
                'level': 'DEBUG',
                'formatter': 'simple',
                'encoding': 'utf8'
            },
        'console_handler':
            {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'simple'
            }
    },

    root={
        'handlers': ['console_handler', 'file_handler'],
        'level': logging.DEBUG,
    }
)
# logging.getLogger('sqlalchemy.engine').setLevel(logging.WARN)
# logging.getLogger('urllib3.connectionpool').setLevel(logging.INFO)
dictConfig(logging_config)

if __name__ == "__main__":
    pass
