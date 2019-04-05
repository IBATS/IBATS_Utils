#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 19-4-4 上午11:44
@File    : test_mess.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import unittest
from ibats_utils.mess import pattern_datatime_format


class PatternDatatimeFormatTest(unittest.TestCase):  # 继承unittest.TestCase

    def test_func(self):
        # '%Y-%m-%d %H:%M:%S.%f'
        dt = pattern_datatime_format('2018-12-31 11:23:56.123')
        self.assertEqual(dt, '%Y-%m-%d %H:%M:%S.%f')
        dt = pattern_datatime_format('2018-2-1 11:23:56.123')
        self.assertEqual(dt, '%Y-%m-%d %H:%M:%S.%f')
        dt = pattern_datatime_format('2018-2-1 1:2:5.123')
        self.assertEqual(dt, '%Y-%m-%d %H:%M:%S.%f')

        # '%Y-%m-%d %H:%M:%S'
        dt = pattern_datatime_format('2018-12-31 11:23:56')
        self.assertEqual(dt, '%Y-%m-%d %H:%M:%S')
        dt = pattern_datatime_format('2018-2-1 11:23:56')
        self.assertEqual(dt, '%Y-%m-%d %H:%M:%S')
        dt = pattern_datatime_format('2018-2-1 1:2:5')
        self.assertEqual(dt, '%Y-%m-%d %H:%M:%S')

        # '%Y%m%d %H%M%S'
        dt = pattern_datatime_format('20181231 112356')
        self.assertEqual(dt, '%Y%m%d %H%M%S')
        dt = pattern_datatime_format('20181231 112356.123')
        self.assertEqual(dt, '%Y%m%d %H%M%S.%f')
        dt = pattern_datatime_format('20181231 11-23-56')
        self.assertEqual(dt, '%Y%m%d %H-%M-%S')


if __name__ == '__main__':
    unittest.main()  # 运行所有的测试用例
