#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2018/6/14 16:07
@File    : setup.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as rm:
    long_description = rm.read()

setup(name='IBATS_Utils',
      version='1.2.13',
      description='IBATS 通用工具，该工具涉及数据库、量化、以及一些通用工具',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='MG',
      author_email='mmmaaaggg@163.com',
      url='https://github.com/IBATS/IBATS_Utils',
      packages=find_packages(),
      python_requires='>=3.6',
      classifiers=(
          "Programming Language :: Python :: 3 :: Only",
          "Programming Language :: Python :: 3.6",
          "Programming Language :: Python :: 3.7",
          "Operating System :: Microsoft :: Windows",
          "Operating System :: Unix",
          "Operating System :: POSIX",
          "License :: OSI Approved :: MIT License",
          "Development Status :: 5 - Production/Stable",
          "Environment :: No Input/Output (Daemon)",
          "Intended Audience :: Developers",
          "Natural Language :: Chinese (Simplified)",
          "Topic :: Software Development",
      ),
      install_requires=[
          'pandas>=0.23.0',
          'redis>=2.10.6',
          'SQLAlchemy>=1.2.8',
          'xlrd>=1.1.0',
          'matplotlib>=3.0.3',
          'numba>=0.51.2',
      ])
