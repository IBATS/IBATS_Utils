#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 19-4-4 上午11:44
@File    : test_mess.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import time
import unittest
from ibats_utils.mess import pattern_datatime_format, try_n_times, decorator_timer
import logging

# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s %(name)s|%(funcName)s:%(lineno)d %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


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


class TryNTimesTest(unittest.TestCase):  # 继承unittest.TestCase

    def setUp(self):
        # 每个测试用例执行之前做操作
        self.try_count = 0

    def test_try_n_times(self):
        @try_n_times(times=3, logger=logger, timeout=1)
        def func():
            self.try_count += 1
            logger.debug("call func %d", self.try_count)
            if self.try_count <= 2:
                # 前N次尝试，每次被调用时睡眠3秒钟
                times = 0
                while True:
                    time.sleep(0.1)
                    times += 1
                    if times >= 40:
                        break

            logger.debug("call func %d return", self.try_count)
            return self.try_count

        ret_data = func()
        logger.info("ret_data = %d", ret_data)
        self.assertEqual(ret_data, 3)


class DecoratorTimerTest(unittest.TestCase):  # 继承unittest.TestCase

    def test_func(self):
        @decorator_timer
        def func1(num):
            time.sleep(num)
            return num

        self.assertEqual(func1(10), 10)


if __name__ == '__main__':
    unittest.main()  # 运行所有的测试用例

