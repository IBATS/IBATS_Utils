#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 2016/12/12 14:47
@File    : mess.py
@contact : mmmaaaggg@163.com
@desc    :
"""
import os
import time
import functools
from datetime import datetime, date, timedelta
import pytz
import numpy as np
import re
import pandas as pd
from collections import OrderedDict
import logging
import warnings
from functools import reduce
import xlrd
import threading
import math
import platform
from matplotlib.font_manager import FontManager
import subprocess
import importlib
import shutil
import random
from numba import njit

logger = logging.getLogger(__name__)
STR_FORMAT_DATE = '%Y-%m-%d'
STR_FORMAT_DATETIME = '%Y-%m-%d %H:%M:%S'
STR_FORMAT_DATETIME2 = '%Y-%m-%d %H:%M:%S.%f'
STR_FORMAT_TIME = '%H:%M:%S'
PATTERN_DATE_FORMAT_RESTRICT = re.compile(r"\d{4}(\D)*\d{2}(\D)*\d{2}")
PATTERN_DATE_FORMAT = re.compile(r"\d{4}(\D)+\d{1,2}(\D)+\d{1,2}")
PATTERN_DATETIME_F_FORMAT_RESTRICT = re.compile(r"\d{4}(\D)*\d{2}(\D)*\d{2} \d{2}(\D)*\d{2}(\D)*\d{2}(\D)+\d{3,6}")
PATTERN_DATETIME_F_FORMAT = re.compile(r"\d{4}(\D)+\d{1,2}(\D)+\d{1,2} \d{1,2}(\D)+\d{1,2}(\D)+\d{1,2}(\D)+\d{1,6}")
PATTERN_DATETIME_FORMAT_RESTRICT = re.compile(r"\d{4}(\D)*\d{2}(\D)*\d{2} \d{2}(\D)*\d{2}(\D)*\d{2}")
PATTERN_DATETIME_FORMAT = re.compile(r"\d{4}(\D)*\d{1,2}(\D)*\d{1,2} \d{1,2}(\D)*\d{1,2}(\D)*\d{1,2}")


def thread_save(func):
    """线程安全装饰器，用于该函数执行过程线程安全"""
    lock = threading.Lock()

    def wrapper(*args, **kwargs):
        with lock:
            func(*args, **kwargs)

    return wrapper


def active_coroutine(func):
    """装饰器：向前执行第一个 yield 表达式，预激活 func"""
    @functools.wraps(func)
    def primer(*arg, **kwargs):
        gen = func(*arg, **kwargs)
        next(gen)
        return gen

    return primer


def floor(x, precision=0):
    """带小数位精度控制的 floor"""
    if precision == 0:
        return math.floor(x)
    else:
        return math.floor(x * (10 ** precision)) / (10 ** precision)


def ceil(x, precision=0):
    """带小数位精度控制的 ceil"""
    if precision == 0:
        return math.ceil(x)
    else:
        return math.ceil(x * (10 ** precision)) / (10 ** precision)


def range_date(start: date, end: date, step=1):
    if start > end:
        return
    ret_date = start
    while ret_date <= end:
        yield ret_date
        ret_date += timedelta(days=step)

    if ret_date > end:
        yield end


def is_any(iterable, func):
    """
    查找是否存在任何一个为True的结果，否则返回False
    :param iterable:
    :param func:
    :return:
    """
    for x in iterable:
        if func(x):
            return True
    else:
        return False


def is_not_nan_or_none(x):
    """
    判断是否不是 NAN 或 None
    :param x:
    :return:
    """
    return False if x is None else not ((isinstance(x, float) and np.isnan(x)) or pd.isna(x))


def is_nan_or_none(x):
    """
    判断是否是 NAN 或 None
    :param x:
    :return:
    """
    return True if x is None else (isinstance(x, float) and np.isnan(x)) or pd.isna(x)


def try_2_float(data):
    try:
        return None if data is None else float(data)
    except:
        logger.exception('%s 转化失败', data)
        return None


def split_chunk(l: list, n: int):
    """
    将数组按照给定长度进行分割
    :param l:
    :param n:
    :return:
    """
    for i in range(0, len(l), n):
        yield l[i:i + n]


def iter_2_range(iterator, has_left_outer=True, has_right_outer=True):
    """
    将一个 N 长度的 iterator 生成 N + 1 个区间
    例如：[1,2,3] --> [[None, 1], [1, 2] [2, 3] [3, None]]
    :param iterator:
    :param has_left_outer:
    :param has_right_outer:
    :return:
    """
    last_val = None
    for val in iterator:
        if last_val is not None or has_left_outer:
            yield last_val, val
        last_val = val
    else:
        if last_val is not None and has_right_outer:
            yield last_val, None


def zip_split(*args, sep=','):
    """
    将多个字符串，按照 sep 分割对齐，形成元祖数组
    :param args: [str1, str2, ...]
    :param sep: 默认 ,
    :return:
    """
    return list(zip(*[arg.split(sep=sep) for arg in args]))


def unzip_join(tuple_list, sep=','):
    return (sep.join(arg) for arg in zip(*tuple_list))


def populate_obj(model_obj, data_dic: dict, attr_list=None, error_if_no_key=False):
    """
    通过 dict 设置模型对应的属性
    :param model_obj:
    :param data_dic:
    :param attr_list:
    :param error_if_no_key:
    :return:
    """
    for name in (attr_list if attr_list is not None else data_dic.keys()):
        if name in data_dic:
            setattr(model_obj, name, data_dic[name])
        elif error_if_no_key:
            raise KeyError("data_dic 缺少 '%s' key 无法设置到 %s" % (name, model_obj.__class__.__name__))
        else:
            warnings.warn("data_dic 缺少 '%s' key 无法设置到 %s" % (name, model_obj.__class__.__name__))


def log_param_when_exception(func):

    @functools.wraps(func)
    def handler(*arg, **kwargs):
        try:
            return func(*arg, **kwargs)
        except Exception as exp:
            msg = '%s(%s, %s)' % (
                func.__name__,
                ', '.join([str(v) for v in arg]),
                ', '.join(
                    ['{key}={value}'.format(key=str(key), value=str(value))
                     for key, value in kwargs.items()]
                )
            )
            logger.exception(msg)
            raise exp from exp

    return handler


def str_2_float(sth) -> (float, None):
    """将数据转换成 float 类型，如果是None， NAT， NAN等数据就变成 None"""
    try:
        ret_val = None if is_nan_or_none(sth) else float(sth)
    except TypeError:
        ret_val = sth

    return ret_val


def format_2_str(value, formator):
    """根据 formator 将对象格式化成 str"""
    if formator is None:
        text = str(value)
    elif isinstance(formator, str):
        text = str.format(formator, value)
    elif callable(formator):
        text = formator(value)
    else:
        raise ValueError('%s: %s 无效', value, formator)
    return text


class TryThread(threading.Thread):

    def __init__(self, target, *args, **kwargs):
        threading.Thread.__init__(self, target=target, args=args, kwargs=kwargs, name="try_thread")
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.ret = None

    def run(self):
        self.ret = self.target(*self.args, **self.kwargs)


def try_n_times(times=3, sleep_time=3, logger: logging.Logger = None, exception=Exception, exception_sleep_time=0,
                timeout=None):
    """
    尝试最多 times 次，异常捕获记录后继续尝试
    :param times:
    :param sleep_time:
    :param logger: 如果异常需要 log 记录则传入参数
    :param exception: 可用于捕获指定异常，默认 Exception
    :param exception_sleep_time: 当出现异常情况下，sleep n 秒
    :param timeout: 超时时间
    :return:
    """
    last_invoked_time = [None]

    def wrap_func(func):

        @functools.wraps(func)
        def try_it(*arg, **kwargs):
            ret_data = None
            for n in range(1, times + 1):
                if sleep_time > 0 and last_invoked_time[0] is not None \
                        and (time.time() - last_invoked_time[0]) < sleep_time:
                    time.sleep(sleep_time - (time.time() - last_invoked_time[0]))

                try:
                    if timeout is None or timeout <= 0:
                        ret_data = func(*arg, **kwargs)
                    else:
                        thread = TryThread(target=func, *arg, **kwargs)
                        thread.start()
                        wait_time = 0
                        while wait_time < timeout:
                            if thread.is_alive():
                                time.sleep(0.2)
                                wait_time += 0.2
                            else:
                                ret_data = thread.ret
                                break
                        else:
                            if logger is not None:
                                logger.warning("执行任务超时限(%ds)", timeout)
                            thread.join()
                            if logger is not None:
                                logger.warning("终止任务完成")
                            continue

                except exception:
                    if logger is not None:
                        logger.exception("第 %d 次调用 %s(%s, %s) 出错", n, func.__name__, arg, kwargs)
                    if exception_sleep_time is not None and exception_sleep_time > 0:
                        time.sleep(exception_sleep_time)
                    continue
                finally:
                    last_invoked_time[0] = time.time()

                break

            return ret_data

        return try_it

    return wrap_func


def date_2_str(dt, format=STR_FORMAT_DATE):
    """将日期类型转换为字符串"""
    if dt is not None and type(dt) in (date, datetime, pd.Timestamp):
        dt_str = dt.strftime(format)
    else:
        dt_str = dt
    return dt_str


def datetime_2_str(dt, format=STR_FORMAT_DATETIME):
    if dt is not None and type(dt) in (date, datetime, pd.Timestamp):
        dt_str = dt.strftime(format)
        # print(type(dt), '->', dt_str)
    elif isinstance(dt, pd.DatetimeIndex):
        dt_str = [x.strftime(format) for x in dt]
        # print(type(dt), '-->', dt_str)
    else:
        dt_str = dt
        # print(type(dt), '没有转换', dt)
    return dt_str


def time_2_str(t):
    if t is not None and isinstance(t, timedelta):
        seconds = t.seconds
        hours, minutes = divmod(seconds, 3600)
        minutes, secs = divmod(minutes, 60)
        dt_str = "{0:02d}:{1:02d}:{2:02d}".format(hours, minutes, secs)
        # print(type(t), '->', dt_str)
    else:
        dt_str = str(t)
        # print(type(t), '没有转换', t)
    return dt_str


def date_time_2_str(d, t):
    """将日期与时间组合成  '%Y-%m-%d %H:%M:%S' 字符串 """
    return date_2_str(d) +  ' ' + time_2_str(t)


def str_2_datetime(datetime_str, format=STR_FORMAT_DATETIME):
    if datetime_str is not None:
        if type(datetime_str) == str:
            date_ret = datetime.strptime(datetime_str, format)
        elif type(datetime_str) in (pd.Timestamp, datetime):
            date_ret = datetime_str
        else:
            date_ret = datetime_str
    else:
        date_ret = datetime_str
    return date_ret


def str_2_bytes(input_str):
    """
    用于将 str 类型转换为 bytes 类型
    :param input_str:
    :return:
    """
    return input_str.encode(encoding='GBK')


def bytes_2_str(bytes_str):
    """
    用于将bytes 类型转换为 str 类型
    :param bytes_str:
    :return:
    """
    return str(bytes_str, encoding='GBK')


def timedelta_2_str(td):
    """
    用于将 pd.Timedelta 类型转换为 str 类型
    :param td:
    :return:
    """
    if isinstance(td, pd.Timedelta):
        ret = str(td).split()[-1]
    else:
        ret = td
    return ret


def pattern_data_format(data_str):
    """
    识别日期格式（例如：2017-12-23），并将其翻译成 %Y-%m-%d 类似的格式
    :param data_str:
    :return:
    """
    date_str_format = PATTERN_DATE_FORMAT_RESTRICT.sub(r'%Y\1%m\2%d', data_str)
    if date_str_format == data_str:
        date_str_format = PATTERN_DATE_FORMAT.sub(r'%Y\1%m\2%d', data_str)
    return date_str_format


def pattern_datatime_format(data_str):
    """
    识别日期格式（例如：2017-12-23 12:31:56），并将其翻译成 %Y-%m-%d %H:%M:%S 类似的格式
    识别日期格式（例如：2017-12-23 12:31:56.123），并将其翻译成 %Y-%m-%d %H:%M:%S.%f 类似的格式
    :param data_str:
    :return:
    """
    # 带 %f
    date_str_format = PATTERN_DATETIME_F_FORMAT_RESTRICT.sub(r'%Y\1%m\2%d %H\3%M\4%S\5%f', data_str)
    if date_str_format != data_str:
        return date_str_format

    date_str_format = PATTERN_DATETIME_F_FORMAT.sub(r'%Y\1%m\2%d %H\3%M\4%S\5%f', data_str)
    if date_str_format != data_str:
        return date_str_format

    # 不带 %f
    date_str_format = PATTERN_DATETIME_FORMAT_RESTRICT.sub(r'%Y\1%m\2%d %H\3%M\4%S', data_str)
    if date_str_format != data_str:
        return date_str_format
    date_str_format = PATTERN_DATETIME_FORMAT.sub(r'%Y\1%m\2%d %H\3%M\4%S', data_str)
    if date_str_format != data_str:
        return date_str_format

    return date_str_format


def try_2_date(something):
    """
    兼容各种格式尝试将 未知对象转换为 date 类型，相对比 str_2_date 消耗资源，支持更多的类型检查，字符串格式匹配
    :param something:
    :return:
    """
    if something is None:
        date_ret = something
    else:
        something_type = type(something)
        if something_type in (int, np.int64, np.int32, np.int16, np.int8):
            something = str(something)
            something_type = type(something)
        if type(something) == str:
            date_str_format = pattern_data_format(something)
            date_ret = datetime.strptime(something, date_str_format).date()
        elif type(something) in (pd.Timestamp, datetime):
            date_ret = something.date()
        else:
            date_ret = something
    return date_ret


def try_2_datetime(something):
    """
    兼容各种格式尝试将 未知对象转换为 date 类型，相对比 str_2_date 消耗资源，支持更多的类型检查，字符串格式匹配
    :param something:
    :return:
    """
    if something is None:
        date_ret = something
    else:
        something_type = type(something)
        if something_type in (int, np.int64, np.int32, np.int16, np.int8):
            something = str(something)
            something_type = type(something)
        if type(something) == str:
            date_str_format = pattern_datatime_format(something)
            date_ret = datetime.strptime(something, date_str_format).date()
        elif isinstance(something, datetime):
            date_ret = something
        elif isinstance(something, pd.Timestamp):
            date_ret = something.to_pydatetime()
        else:
            date_ret = something
    return date_ret


def pd_timedelta_2_timedelta(value):
    if isinstance(value, pd.Timedelta):
        # print(value, 'parse to timedelta')
        dt_value = timedelta(seconds=value.seconds)
    else:
        dt_value = value
    return dt_value


def get_first(iterable, func, ret_func=None):
    for val in iterable:
        if func(val):
            return val if ret_func is None else ret_func(val)
    return None


def get_first_idx(iterable, func):
    for idx, n in enumerate(iterable):
        if func(n):
            return idx
    return None


@njit
def get_first_idx_larger_than(arr: np.ndarray, k):
    for i in range(len(arr)):
        if arr[i] > k:
            return i
    return -1


@njit
def get_first_idx_smaller_than(arr: np.ndarray, k):
    for i in range(len(arr)):
        if arr[i] < k:
            return i
    return -1


def get_last(iterable, comp_func, ret_func=None):
    count = len(iterable)
    for n in range(count - 1, -1, -1):
        val = iterable[n]
        if comp_func(val):
            return val if ret_func is None else ret_func(val)
    return None


def get_last_idx(iterable, func):
    """
    获取最后一个符合条件数据的数组索引
    :param iterable:
    :param func:
    :return:
    """
    count = len(iterable)
    for n in range(count - 1, -1, -1):
        if func(iterable[n]):
            return n
    return None


@njit
def get_last_idx_larger_than(arr: np.ndarray, k):
    for i in range(len(arr) - 1, -1, -1):
        if arr[i] > k:
            return i
    return -1


@njit
def get_last_idx_smaller_than(arr: np.ndarray, k):
    for i in range(len(arr) - 1, -1, -1):
        if arr[i] < k:
            return i
    return -1


@njit
def get_nth_index(arr: np.ndarray, func, count):
    c = 0
    for i in range(len(arr)):
        if func(arr[i]):
            c += 1
            if c == count:
                return i
    return -1


@njit
def get_nth_index_right(arr: np.ndarray, func, count):
    c = 0
    for i in range(len(arr) - 1, -1, -1):
        if func(arr[i]):
            c += 1
            if c == count:
                return i
    return -1


def _test_get_idx_nb():
    np.random.seed(0)
    arr = np.random.rand(10 ** 7)
    m = 0.999999
    n = 0.9999999
    # # Start of array benchmark
    # % timeit next(iter(np.where(arr > m)[0]), -1)  # 43.5 ms
    # % timeit next((idx for idx, val in enumerate(arr) if val > m), -1)  # 2.5 µs
    # # End of array benchmark
    # % timeit next(iter(np.where(arr > n)[0]), -1)  # 21.4 ms
    # % timeit next((idx for idx, val in enumerate(arr) if val > n), -1)  # 39.2 ms
    idx = get_first_idx_larger_than(arr, n)
    assert idx == -1
    idx = get_first_idx_smaller_than(arr, 1 - n)
    assert idx == 3600965
    idx = get_last_idx_larger_than(arr, n)
    assert idx == -1
    idx = get_last_idx_smaller_than(arr, 1 - n)
    assert idx == 3600965

    idx = get_first_idx_larger_than(arr, m)
    assert idx == 198253
    idx = get_first_idx_smaller_than(arr, 1 - m)
    assert idx == 661553
    idx = get_last_idx_larger_than(arr, m)
    assert idx == 8361873
    idx = get_last_idx_smaller_than(arr, 1 - m)
    assert idx == 6590717

    @njit
    def func(val):
        return val > m

    idx = get_nth_index(arr, func, 2)
    assert idx == 801807
    idx = get_nth_index_right(arr, func, 2)
    assert idx == 8142781


def replace_none_2_str(string, replace=''):
    return replace if string is None else string


def str_2_date(date_str, date_str_format=STR_FORMAT_DATE):
    """
    将日期字符串转换成 date 类型对象，如果字符串为 None 则返回None
    :param date_str: 日期字符串
    :param date_str_format: 日期字符串格式
    :return:
    """
    if date_str is not None:
        if type(date_str) == str:
            date_ret = datetime.strptime(date_str, date_str_format).date()
        elif type(date_str) in (pd.Timestamp, datetime):
            date_ret = date_str.date()
        else:
            date_ret = date_str
    else:
        date_ret = date_str
    return date_ret


def date2datetime(dt):
    """
    date 类型转换问 datetime类型
    :param dt:
    :return:
    """
    return datetime(dt.year, dt.month, dt.day)


def clean_datetime_remove_time_data(atime):
    """
    将时间对象的 时、分、秒 全部清零
    :param atime:
    :return:
    """
    return datetime(atime.year, atime.month, atime.day)


def clean_datetime_remove_ms(atime):
    """
    将时间对象的 毫秒 全部清零
    :param atime:
    :return:
    """
    return datetime(atime.year, atime.month, atime.day, atime.hour, atime.minute, atime.second)


def utc2local(utc):
    localtime = datetime.utcfromtimestamp(utc).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Shanghai'))
    return localtime


def get_cntr_kind_name(contract_name):
    left_idx = len(contract_name) - 1
    for num_str in '1234567890':
        idx = contract_name.find(num_str, 0, left_idx)
        if idx == -1:
            continue
        if idx < left_idx:
            left_idx = idx
        if left_idx <= 1:
            break
    # print(lidx, contractname[:lidx])
    return contract_name[:left_idx]


CACHE_FOLDER_PATH_DIC = {}


def is_pattern_type(obj):
    """
    判断当前对象是否是 Pattern 类
    3.7以后 re._pattern_type 被废弃，re.Pattern开始启用。此写法为了兼容3.6. 以及 3.7 以后版本
    :param obj:
    :return:
    """
    try:
        return isinstance(obj, re.Pattern)
    except AttributeError:
        return isinstance(obj, re._pattern_type)


def get_folder_path(target_folder_name=None, create_if_not_found=True):
    """
    获得系统缓存目录路径
    :param target_folder_name: 缓存目录名称 或 正则表达式
    :param create_if_not_found: 如果不存在则创建一个目录，默认：True，当 target_folder_name 为正则表达式时，无法创建目录
    :return: 缓存路径
    """
    global CACHE_FOLDER_PATH_DIC
    if target_folder_name is None:
        target_folder_name = 'cache'
    if target_folder_name not in CACHE_FOLDER_PATH_DIC:
        cache_folder_path_tmp = None
        logger.debug('查找数据目录path:')
        parent_folder_path = os.path.abspath(os.curdir)
        par_path = parent_folder_path
        while not os.path.ismount(par_path):
            # print 'parent path = %s'%par_path
            dir_list = os.listdir(par_path)
            for dir_name in dir_list:
                # print d # .strip()
                if is_pattern_type(target_folder_name):
                    match = target_folder_name.match(dir_name)
                    if match is not None:
                        cache_folder_path_tmp = os.path.join(par_path, dir_name)
                        logger.debug('<%s>', cache_folder_path_tmp)
                        break
                elif dir_name == target_folder_name:
                    cache_folder_path_tmp = os.path.join(par_path, dir_name)
                    logger.debug('<%s>', cache_folder_path_tmp)
                    break
            if cache_folder_path_tmp is not None:
                break
            par_path = os.path.abspath(os.path.join(par_path, os.path.pardir))
        if cache_folder_path_tmp is None:
            if create_if_not_found and not is_pattern_type(target_folder_name):
                cache_folder_path_tmp = os.path.abspath(os.path.join(parent_folder_path, target_folder_name))
                logger.debug('<%s> 创建缓存目录', cache_folder_path_tmp)
                os.makedirs(cache_folder_path_tmp)
                CACHE_FOLDER_PATH_DIC[target_folder_name] = cache_folder_path_tmp
        else:
            CACHE_FOLDER_PATH_DIC[target_folder_name] = cache_folder_path_tmp
    return CACHE_FOLDER_PATH_DIC.setdefault(target_folder_name, None)


def get_cache_file_path(cache_folder_name, file_name, create_if_not_found=True):
    """
    返回缓存文件的路径
    :param file_name: 缓存文件名称
    :param cache_folder_name: 缓存folder名称
    :param create_if_not_found: 如果不存在则创建一个目录，默认：True
    :return: 缓存文件路径
    """
    cache_folder_path = get_folder_path(cache_folder_name, create_if_not_found)
    return os.path.join(cache_folder_path, file_name)


def get_df_between_date(data_df, date_frm, date_to):
    """
    该函数仅用于 return_risk_analysis 中计算使用
    :param data_df:
    :param date_frm:
    :param date_to:
    :return:
    """
    if date_frm is not None and date_to is not None:
        new_data_df = data_df[(data_df.Date >= date_frm) & (data_df.Date <= date_to)]
    elif date_frm is not None:
        new_data_df = data_df[data_df.Date >= date_frm]
    elif date_to is not None:
        new_data_df = data_df[data_df.Date <= date_to]
    else:
        new_data_df = data_df
    new_data_df = new_data_df.reset_index(drop=True)
    return new_data_df


def _get_df_between_date_by_index(data_df, date_frm, date_to):
    """
    该函数仅用于 return_risk_analysis 中计算使用
    :param data_df:
    :param date_frm:
    :param date_to:
    :return:
    """
    if date_frm is not None and date_to is not None:
        new_data_df = data_df[(data_df.index >= date_frm) & (data_df.index <= date_to)]
    elif date_frm is not None:
        new_data_df = data_df[data_df.index >= date_frm]
    elif date_to is not None:
        new_data_df = data_df[data_df.index <= date_to]
    else:
        new_data_df = data_df
    return new_data_df


def return_risk_analysis_old(nav_df: pd.DataFrame, date_frm=None, date_to=None, freq='weekly', rf=0.02):
    """
    按列统计 rr_df 收益率绩效
    :param nav_df: 收益率DataFrame，index为日期，每一列为一个产品的净值走势
    :param date_frm: 统计日期区间，可以为空
    :param date_to: 统计日期区间，可以为空
    :param freq: None 自动识别, 'daily' 'weekly' 'monthly'
    :param rf: 无风险收益率，默认 0.02
    :return:
    """
    nav_df.index = [try_2_date(idx) for idx in nav_df.index]
    nav_sorted_df = nav_df.sort_index()
    rr_df = (1 + nav_sorted_df.pct_change().fillna(0)).cumprod()
    rr_df.index = [try_2_date(d) for d in rr_df.index]
    # 计算数据实际频率是日频、周频、月頻
    rr_df_len = rr_df.shape[0]
    day_per_data = (rr_df.index[rr_df_len - 1] - rr_df.index[0]).days / rr_df_len
    if day_per_data <= 0.005:
        freq_real = 'minute'
    elif day_per_data <= 0.2:
        freq_real = 'hour'
    elif day_per_data <= 2:
        freq_real = 'daily'
    elif day_per_data <= 10:
        freq_real = 'weekly'
    else:
        freq_real = 'monthly'
    if freq is None:
        freq = freq_real
    elif freq != freq_real:
        warnings_msg = "data freq wrong, expect %s, but %s was detected" % (freq, freq_real)
        # warnings.warn(warnings_msg)
        # logging.warning(warnings_msg)
        raise ValueError(warnings_msg)

    freq_str = ''
    if freq == 'weekly':
        data_count_per_year = 50
        freq_str = '周'
    elif freq == 'monthly':
        data_count_per_year = 12
        freq_str = '月'
    elif freq == 'daily':
        data_count_per_year = 250
        freq_str = '日'
    elif freq == 'hour':
        data_count_per_year = 1250
        freq_str = '时'
    elif freq == 'minute':
        data_count_per_year = 75000
        freq_str = '分'
    else:
        raise ValueError('freq=%s 只接受 daily weekly monthly 三种之一', freq)
    stat_dic_dic = OrderedDict()
    # rr_df.index = [str_2_date(d) for d in rr_df.index]
    rr_uindex_df = rr_df.reset_index()
    col_name_list = list(rr_uindex_df.columns)
    date_col_name = col_name_list[0]
    col_name_list = col_name_list[1:]
    if type(date_frm) is str:
        date_frm = datetime.strptime(date_frm, '%Y-%m-%d').date()
    if type(date_to) is str:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    for col_name in col_name_list:
        data_df = rr_uindex_df[[date_col_name, col_name]]
        # print(data_df)
        data_df.columns = ['Date', 'Value']
        data_df = get_df_between_date(data_df, date_frm, date_to)
        data_df.Value = data_df.Value / data_df.Value[0]
        data_df['ret'] = data_df.Value.pct_change().fillna(0)
        date_span = data_df.Date[data_df.index[-1]] - data_df.Date[data_df.index[0]]
        date_span_fraction = 365 / date_span.days if date_span.days > 0 else 1
        # basic indicators
        CAGR = data_df.Value[data_df.index[-1]] ** date_span_fraction - 1
        period_rr = data_df.Value[data_df.index[-1]] - 1
        ann_vol = np.std(data_df.ret, ddof=1) * np.sqrt(data_count_per_year)
        down_side_vol = np.std(data_df.ret[data_df.ret < 0], ddof=1) * np.sqrt(data_count_per_year)
        # WeeksNum = data.shape[0]
        profit_loss_ratio = -np.mean(data_df.ret[data_df.ret > 0]) / np.mean(data_df.ret[data_df.ret < 0])
        win_ratio = len(data_df.ret[data_df.ret >= 0]) / len(data_df.ret)
        min_value = min(data_df.Value)
        final_value = data_df.Value[data_df.index[-1]]
        max_ret = max(data_df.ret)
        min_ret = min(data_df.ret)
        # End of basic indicators
        # max dropdown related
        data_df['mdd'] = data_df.Value / data_df.Value.cummax() - 1
        mdd_size = min(data_df.mdd)
        droparray = pd.Series(data_df.index[data_df.mdd == 0])
        if len(droparray) == 1:
            mdd_max_period = len(data_df.mdd)
        else:
            if float(data_df.Value[droparray.tail(1)]) > float(data_df.Value.tail(1)):
                droparray = droparray.append(pd.Series(data_df.index[-1]), ignore_index=True)
            mdd_max_period = max(droparray.diff().dropna()) - 1
        # End of max dropdown related
        # High level indicators
        sharpe_ratio = (CAGR - rf) / ann_vol
        sortino_ratio = (CAGR - rf) / down_side_vol
        calmar_ratio = CAGR / (-mdd_size)
        #  Natural month return
        j = 1
        for i in data_df.index:
            if i == 0:
                month_ret = pd.DataFrame([[data_df.Date[i], data_df.Value[i]]], columns=('Date', 'Value'))
            else:
                if data_df.Date[i].month != data_df.Date[i - 1].month:
                    month_ret.loc[j] = [data_df.Date[i - 1], data_df.Value[i - 1]]
                    j += 1
        month_ret.loc[j] = [data_df.Date[data_df.index[-1]], data_df.Value[data_df.index[-1]]]
        month_ret['ret'] = month_ret.Value.pct_change().fillna(0)
        max_rr_month = max(month_ret.ret)
        min_rr_month = min(month_ret.ret)
        # End of Natural month return
        data_len = data_df.shape[0]
        date_begin = data_df.Date[0]  # .date()
        date_end = data_df.Date[data_len - 1]
        stat_dic = OrderedDict([('起始日期', date_begin),
                                ('截止日期', date_end),
                                ('区间收益率', '%.2f%%' % (period_rr * 100)),
                                ('最终净值', '%.4f' % final_value),
                                ('最低净值', '%.4f' % min_value),
                                ('年化收益率', '%.2f%%' % (CAGR * 100)),
                                ('年化波动率', '%.2f%%' % (ann_vol * 100)),
                                ('年化下行波动率', '%.2f%%' % (down_side_vol * 100)),
                                ('最大回撤', '%.2f%%' % (mdd_size * 100)),
                                ('夏普率', '%.2f' % sharpe_ratio),
                                ('索提诺比率', '%.2f' % sortino_ratio),
                                ('卡马比率', '%.2f' % calmar_ratio),
                                ('盈亏比', '%.2f' % profit_loss_ratio),
                                ('胜率', '%.2f' % win_ratio),
                                ('最长不创新高（%s）' % freq_str, mdd_max_period),
                                ('统计周期最大收益', '%.2f%%' % (max_ret * 100)),
                                ('统计周期最大亏损', '%.2f%%' % (min_ret * 100)),
                                ('最大月收益', '%.2f%%' % (max_rr_month * 100)),
                                ('最大月亏损', '%.2f%%' % (min_rr_month * 100))])
        stat_dic_dic[col_name] = stat_dic
    stat_df = pd.DataFrame(stat_dic_dic)
    stat_df = stat_df.ix[list(stat_dic.keys())]
    return stat_df


def calc_performance(nav_df: pd.DataFrame, date_frm=None, date_to=None, freq='weekly', rf=0.02, suffix_name=None):
    """
    按列统计 rr_df 收益率绩效
    :param nav_df: 收益率DataFrame，index为日期，每一列为一个产品的净值走势
    :param date_frm: 统计日期区间，可以为空
    :param date_to: 统计日期区间，可以为空
    :param freq: None 自动识别, 'daily' 'weekly' 'monthly'
    :param rf: 无风险收益率，默认 0.02
    :return:
    """
    nav_sorted_df = nav_df.copy()
    nav_sorted_df.index = [try_2_date(idx) for idx in nav_sorted_df.index]
    nav_sorted_df.sort_index(inplace=True)
    # 计算数据实际频率是日频、周频、月頻
    data_count = nav_sorted_df.shape[0]
    day_per_data = (nav_sorted_df.index[data_count - 1] - nav_sorted_df.index[0]).days / data_count
    if day_per_data <= 0.008:
        freq_real = 'minute'
    elif day_per_data <= 0.2:
        freq_real = 'hour'
    elif day_per_data <= 2:
        freq_real = 'daily'
    elif day_per_data <= 10:
        freq_real = 'weekly'
    else:
        freq_real = 'monthly'
    if freq is None:
        freq = freq_real
    elif freq != freq_real:
        warnings_msg = "data freq wrong, expect %s, but %s was detected" % (freq, freq_real)
        # warnings.warn(warnings_msg)
        # logging.warning(warnings_msg)
        raise ValueError(warnings_msg)

    freq_str = ''
    if freq == 'weekly':
        data_count_per_year = 50
        freq_str = '周'
    elif freq == 'monthly':
        data_count_per_year = 12
        freq_str = '月'
    elif freq == 'daily':
        data_count_per_year = 250
        freq_str = '日'
    elif freq == 'hour':
        data_count_per_year = 1250
        freq_str = '时'
    elif freq == 'minute':
        data_count_per_year = 75000
        freq_str = '分'
    else:
        raise ValueError('freq=%s 只接受 daily weekly monthly 三种之一', freq)
    stat_dic_dic = OrderedDict()
    if type(date_frm) is str:
        date_frm = datetime.strptime(date_frm, '%Y-%m-%d').date()
    if type(date_to) is str:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()

    col_name_list = list(nav_sorted_df.columns)
    # date_col_name = col_name_list[0]
    # col_name_list = col_name_list[1:]
    for col_name in col_name_list:
        data_sub_df = nav_sorted_df[[col_name]].dropna()
        if data_sub_df.shape[0] == 0:
            continue
        # rr_df = (1 + data_sub_df.pct_change().fillna(0)).cumprod()
        # rr_df.index = [try_2_date(d) for d in rr_df.index]
        # data_df = rr_df.reset_index()
        # data_df.columns = ['Date', 'Value']
        # 2018-07-01 不再重置索引，index为日期字段
        data_df = _get_df_between_date_by_index(data_sub_df, date_frm, date_to)
        data_df.columns = ['Value']
        rr_df = data_df.Value.pct_change().fillna(0)
        data_df.Value = (1 + rr_df).cumprod()
        data_df['ret'] = rr_df
        date_list = list(data_df.index)
        date_latest = date_list[-1]
        nav_latest = data_df.Value.loc[date_latest]
        # 计算 近7天，近30天，近365天收益率
        date_week_ago = date_latest - timedelta(days=7)
        date_month_ago = date_latest - timedelta(days=30)
        date_year_ago = date_latest - timedelta(days=365)
        date_week_ago = get_last(date_list, lambda x: x <= date_week_ago)
        date_month_ago = get_last(date_list, lambda x: x <= date_month_ago)
        date_year_ago = get_last(date_list, lambda x: x <= date_year_ago)
        rr_week = (nav_latest / data_df.Value.loc[date_week_ago] - 1) if date_week_ago is not None else None
        rr_month = (nav_latest / data_df.Value.loc[date_month_ago] - 1) if date_month_ago is not None else None
        rr_year = (nav_latest / data_df.Value.loc[date_year_ago] - 1) if date_year_ago is not None else None

        # 计算时间跨度
        date_span = date_list[-1] - date_list[0]
        date_span_fraction = 365 / date_span.days if date_span.days > 0 else 1
        # basic indicators
        CAGR = data_df.Value[date_latest] ** date_span_fraction - 1
        # 相当于余额宝倍数
        times_yeb = (CAGR - 1) / 0.03
        rr_tot = data_df.Value[date_latest] - 1
        ann_vol = np.std(data_df.ret, ddof=1) * np.sqrt(data_count_per_year)
        down_side_vol = np.std(data_df.ret[data_df.ret < 0], ddof=1) * np.sqrt(data_count_per_year)
        # WeeksNum = data.shape[0]
        profit_loss_ratio = -np.mean(data_df.ret[data_df.ret > 0]) / np.mean(data_df.ret[data_df.ret < 0])
        win_ratio = len(data_df.ret[data_df.ret >= 0]) / len(data_df.ret)
        min_value = min(data_df.Value)
        final_value = data_df.Value[data_df.index[-1]]
        max_ret = max(data_df.ret)
        min_ret = min(data_df.ret)
        # End of basic indicators
        # max dropdown related
        data_df['mdd'] = data_df.Value / data_df.Value.cummax() - 1
        mdd_size = min(data_df.mdd)
        droparray = pd.Series(data_df.index[data_df.mdd == 0])
        if len(droparray) == 1:
            mdd_max_period = len(data_df.mdd)
        else:
            if float(data_df.Value[droparray.tail(1)]) > float(data_df.Value.tail(1)):
                droparray = droparray.append(pd.Series(data_df.index[-1]))  # , ignore_index=True
            mdd_max_period = max(droparray.diff().dropna()).days - 1
        # End of max dropdown related
        # High level indicators
        sharpe_ratio = (CAGR - rf) / ann_vol
        sortino_ratio = (CAGR - rf) / down_side_vol
        calmar_ratio = CAGR / (-mdd_size)
        #  Natural month return
        j = 1
        for i, (date_4_df_idx, item) in enumerate(data_df.T.items()):
            if i == 0:
                month_ret = pd.DataFrame([[date_4_df_idx, item.Value]], columns=('Date', 'Value'))
            else:
                date_last_4_last = data_df.index[i - 1]
                if date_4_df_idx.month != date_last_4_last.month:
                    month_ret.loc[j] = [date_last_4_last, data_df.Value[date_last_4_last]]
                    j += 1

        month_ret.loc[j] = [date_latest, nav_latest]
        month_ret['ret'] = month_ret.Value.pct_change().fillna(0)
        max_rr_month = max(month_ret.ret)
        min_rr_month = min(month_ret.ret)
        # End of Natural month return
        date_begin = date_list[0]  # .date()
        date_end = date_list[-1]
        stat_dic = OrderedDict([('date_begen', date_begin),
                                ('date_end', date_end),
                                ('rr_tot', rr_tot),
                                ('rr_week', rr_week),
                                ('rr_month', rr_month),
                                ('rr_year', rr_year),
                                ('final_value', final_value),
                                ('min_value', min_value),
                                ('CAGR', CAGR),
                                ('ann_vol', ann_vol),
                                ('down_side_vol', down_side_vol),
                                ('mdd', mdd_size),
                                ('sharpe_ratio', sharpe_ratio),
                                ('sortino_ratio', sortino_ratio),
                                ('calmar_ratio', calmar_ratio),
                                ('profit_loss_ratio', profit_loss_ratio),  # 盈亏比
                                ('win_ratio', '%.2f' % win_ratio),  # 胜率
                                ('mdd_max_period', mdd_max_period),  # 最长不创新高周期数
                                ('freq', freq_str),  # 周期类型
                                ('max_ret', max_ret),  # 统计周期最大收益
                                ('min_ret', min_ret),  # 统计周期最大亏损
                                ('max_rr_month', max_rr_month),  # 最大月收益
                                ('min_rr_month', min_rr_month),  # 最大月亏损
                                ])
        stat_dic_dic[col_name if suffix_name is None else col_name + "_" + suffix_name] = stat_dic

    return stat_dic_dic


def return_risk_analysis(nav_df: pd.DataFrame, date_frm=None, date_to=None, freq='weekly', rf=0.02, suffix_name=None):
    """
    按列统计 rr_df 收益率绩效
    :param nav_df: 收益率DataFrame，index为日期，每一列为一个产品的净值走势
    :param date_frm: 统计日期区间，可以为空
    :param date_to: 统计日期区间，可以为空
    :param freq: None 自动识别, 'daily' 'weekly' 'monthly'
    :param rf: 无风险收益率，默认 0.02
    :return:
    """
    nav_sorted_df = nav_df.copy()
    nav_sorted_df.index = pd.to_datetime([try_2_date(idx) for idx in nav_sorted_df.index])
    nav_sorted_df.sort_index(inplace=True)
    # 计算数据实际频率是日频、周频、月頻
    data_count = nav_sorted_df.shape[0]
    day_per_data = (nav_sorted_df.index[data_count - 1] - nav_sorted_df.index[0]).days / data_count
    if day_per_data <= 0.008:
        freq_real = 'minute'
    elif day_per_data <= 0.2:
        freq_real = 'hour'
    elif day_per_data <= 2:
        freq_real = 'daily'
    elif day_per_data <= 10:
        freq_real = 'weekly'
    else:
        freq_real = 'monthly'
    if freq is None:
        freq = freq_real
    elif freq != freq_real:
        warnings_msg = "data freq wrong, expect %s, but %s was detected" % (freq, freq_real)
        # warnings.warn(warnings_msg)
        # logging.warning(warnings_msg)
        raise ValueError(warnings_msg)

    freq_str = ''
    if freq == 'weekly':
        data_count_per_year = 50
        freq_str = '周'
    elif freq == 'monthly':
        data_count_per_year = 12
        freq_str = '月'
    elif freq == 'daily':
        data_count_per_year = 250
        freq_str = '日'
    elif freq == 'hour':
        data_count_per_year = 1250
        freq_str = '时'
    elif freq == 'minute':
        data_count_per_year = 75000
        freq_str = '分'
    else:
        raise ValueError('freq=%s 只接受 daily weekly monthly 三种之一', freq)
    stat_dic_dic = OrderedDict()
    mon_rr_dic = {}
    if type(date_frm) is str:
        date_frm = datetime.strptime(date_frm, '%Y-%m-%d').date()
    if type(date_to) is str:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()

    col_name_list = list(nav_sorted_df.columns)
    # date_col_name = col_name_list[0]
    # col_name_list = col_name_list[1:]
    for col_name in col_name_list:
        data_sub_df = nav_sorted_df[[col_name]].dropna()
        if data_sub_df.shape[0] == 0:
            continue
        rr_df = (1 + data_sub_df.pct_change().fillna(0)).cumprod()
        # rr_df.index = [try_2_date(d) for d in rr_df.index]
        data_df = rr_df.reset_index()
        data_df.columns = ['Date', 'Value']
        data_df = get_df_between_date(data_df, date_frm, date_to)
        data_df.Value = data_df.Value / data_df.Value[0]
        data_df['ret'] = data_df.Value.pct_change().fillna(0)
        date_span = data_df.Date[data_df.index[-1]] - data_df.Date[data_df.index[0]]
        date_span_fraction = 365 / date_span.days if date_span.days > 0 else 1
        # basic indicators
        CAGR = data_df.Value[data_df.index[-1]] ** date_span_fraction - 1
        period_rr = data_df.Value[data_df.index[-1]] - 1
        ann_vol = np.std(data_df.ret, ddof=1) * np.sqrt(data_count_per_year)
        down_side_vol = np.std(data_df.ret[data_df.ret < 0], ddof=1) * np.sqrt(data_count_per_year)
        # WeeksNum = data.shape[0]
        profit_loss_ratio = -np.mean(data_df.ret[data_df.ret > 0]) / np.mean(data_df.ret[data_df.ret < 0])
        win_ratio = len(data_df.ret[data_df.ret >= 0]) / len(data_df.ret)
        min_value = min(data_df.Value)
        final_value = data_df.Value[data_df.index[-1]]
        max_ret = max(data_df.ret)
        min_ret = min(data_df.ret)
        # End of basic indicators
        # max dropdown related
        data_df['mdd'] = data_df.Value / data_df.Value.cummax() - 1
        mdd_size = min(data_df.mdd)
        droparray = pd.Series(data_df.index[data_df.mdd == 0])
        if len(droparray) == 1:
            mdd_max_period = len(data_df.mdd)
        else:
            if float(data_df.Value[droparray.tail(1)]) > float(data_df.Value.tail(1)):
                droparray = droparray.append(pd.Series(data_df.index[-1]))  # , ignore_index=True
            mdd_max_period = max(droparray.diff().dropna()) - 1
        # End of max dropdown related
        # High level indicators
        sharpe_ratio = (CAGR - rf) / ann_vol
        sortino_ratio = (CAGR - rf) / down_side_vol
        calmar_ratio = CAGR / (-mdd_size)
        #  Natural month return
        j = 1
        for i in data_df.index:
            if i == 0:
                month_ret = pd.DataFrame([[data_df.Date[i], data_df.Value[i]]], columns=('Date', 'Value'))
            else:
                if data_df.Date[i].month != data_df.Date[i - 1].month:
                    month_ret.loc[j] = [data_df.Date[i - 1], data_df.Value[i - 1]]
                    j += 1
        month_ret.loc[j] = [data_df.Date[data_df.index[-1]], data_df.Value[data_df.index[-1]]]
        month_ret['ret'] = month_ret.Value.pct_change().fillna(0)
        max_rr_month = max(month_ret.ret)
        min_rr_month = min(month_ret.ret)
        # End of Natural month return
        data_len = data_df.shape[0]
        date_begin = data_df.Date[0]  # .date()
        date_end = data_df.Date[data_len - 1]
        stat_dic = OrderedDict([('起始日期', date_begin),
                                ('截止日期', date_end),
                                ('区间收益率', '%.2f%%' % (period_rr * 100)),
                                ('最终净值', '%.4f' % final_value),
                                ('最低净值', '%.4f' % min_value),
                                ('年化收益率', '%.2f%%' % (CAGR * 100)),
                                ('年化波动率', '%.2f%%' % (ann_vol * 100)),
                                ('年化下行波动率', '%.2f%%' % (down_side_vol * 100)),
                                ('最大回撤', '%.2f%%' % (mdd_size * 100)),
                                ('夏普率', '%.2f' % sharpe_ratio),
                                ('索提诺比率', '%.2f' % sortino_ratio),
                                ('卡马比率', '%.2f' % calmar_ratio),
                                ('盈亏比', '%.2f' % profit_loss_ratio),
                                ('胜率', '%.2f' % win_ratio),
                                ('最长不创新高（%s）' % freq_str, mdd_max_period),
                                ('统计周期最大收益', '%.2f%%' % (max_ret * 100)),
                                ('统计周期最大亏损', '%.2f%%' % (min_ret * 100)),
                                ('最大月收益', '%.2f%%' % (max_rr_month * 100)),
                                ('最大月亏损', '%.2f%%' % (min_rr_month * 100))])
        stat_dic_dic[col_name if suffix_name is None else col_name + "_" + suffix_name] = stat_dic

        # 按时间周期进行相关统计
        data_df = data_df.set_index('Date')[['Value']]
        # data_df_g = data_df.groupby(pd.Grouper(freq='M'))
        # TODO: 首月收益未被计算进去，以后再修复
        monthly_rr_df = data_df.resample('M', convention='end').last().pct_change().fillna(0)
        mon_rr_dic[col_name if suffix_name is None else col_name + "_" + suffix_name] = monthly_rr_df

    if len(stat_dic_dic) > 0:
        stat_df = pd.DataFrame(stat_dic_dic)
        stat_df = stat_df.loc[list(stat_dic.keys())]
    else:
        stat_df = None

    return stat_df, mon_rr_dic


class DataFrame(pd.DataFrame):
    def interpolate_inner(self, columns=None, inplace=False):
        if columns is None:
            columns = list(self.columns)
        data = self if inplace else self.copy()
        for col_name in columns:
            index_not_nan = data.index[~np.isnan(data[col_name])]
            if index_not_nan.shape[0] == 0:
                continue
            index_range = (min(index_not_nan), max(index_not_nan))
            # data[col_name][index_range[0]:index_range[1]].interpolate(inplace=True)
            data[col_name][index_range[0]:index_range[1]] = data[col_name][index_range[0]:index_range[1]].interpolate()
        # print(data)
        if ~inplace:
            return data

    def map(self, func):
        row_count, col_count = self.shape
        columns = list(self.columns)
        indexes = list(self.index)
        for col_num in range(col_count):
            col_val = columns[col_num]
            for row_num in range(row_count):
                row_val = indexes[row_num]
                data_val = self.iloc[row_num, col_num]
                self.iloc[row_num, col_num] = func(col_val, row_val, data_val)
        return self


def reduce_list(funx, data_list, initial=None):
    result_list = []

    def reduce_func(x, y):
        # print(x,y)
        result = funx(x, y)
        result_list.append(result)
        return result

    if initial is None:
        reduce(reduce_func, data_list)
    else:
        reduce(reduce_func, data_list, initial)
    return result_list


def _calc_mdd_4_drawback_analysis(pair, y):
    """
    此函数仅供 drawback_analysis 使用
    用于计算最大回撤使用
    :param pair:
    :param y:
    :return:
    """
    max_y_last = pair[0]
    max_y = max_y_last if max_y_last > y else y
    mdd_last = pair[1]
    keep_max = pair[2]
    dd = y / max_y - 1
    if keep_max:
        mdd = dd if dd < mdd_last else mdd_last
    else:
        mdd = dd
    return max_y, mdd, keep_max


def drawback_analysis(data_df, keep_max=False):
    """
    计算给定 DataFrame 数据对应的时间序列最大回撤数据
    :param data_df:
    :return:
    """
    if data_df is None or data_df.shape[0] <= 1:
        mdd_df = None
    else:
        mdd_df = data_df.apply(
            lambda xx: [rr[1] for rr in reduce_list(_calc_mdd_4_drawback_analysis, xx, (xx.iloc[0], 0, keep_max))])
    return mdd_df


def return_risk_analysis_by_xls(file_path, date_col=None, nav_col_list=None, encoding=None):
    """
    读xls文件，对每个sheet进行分析，并最终合并绩效分析报告
    回撤分析分别生成文件显示
    :param file_path:
    :return:
    """
    file_path_no_extention, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.csv':
        is_csv_file = True
    else:
        is_csv_file = False
    if is_csv_file:
        sheet_names = ['sheet1']
    else:
        workbook = xlrd.open_workbook(file_path)
        sheet_names = workbook.sheet_names()

    sheet_mdd_df_dic = {}
    stat_df = None
    sheet_mon_rr_dic = {}
    for sheet_name in sheet_names:
        # if sheet_name not in col_names:
        #     continue
        try:
            index_col = 0
            if isinstance(date_col, str):
                if is_csv_file:
                    raise ValueError('csv 文件不支持 index_col 参数为字符串')
                sheet = workbook.sheet_by_name(sheet_name)
                # 取得日期索引后退出
                col_name = sheet.cell_value(0, index_col)
                while not (col_name is None or col_name == ""):
                    if col_name == date_col:
                        break
                    index_col += 1
                    col_name = sheet.cell_value(0, index_col)
            elif isinstance(date_col, int):
                index_col = date_col
            else:
                index_col = 0
            # 默认第0列为日期
            # sheetname Deprecated since version 0.21.0: Use sheet_name instead
            if is_csv_file:
                data_df = pd.read_csv(file_path, index_col=index_col, encoding=encoding)  # 某些版本使用 sheet_name
            else:
                data_df = pd.read_excel(file_path, index_col=index_col, sheet_name=sheet_name)  # 某些版本使用 sheet_name

            if data_df is None or data_df.shape[0] == 0:
                continue
            if nav_col_list is not None:
                data_df = data_df[nav_col_list]
            # 是否带suffix
            if re.search("[S|s]heet", sheet_name) is None:
                suffix_name = sheet_name
            else:
                suffix_name = None
            stat_df_tmp, mon_rr_dic = return_risk_analysis(data_df, freq=None,
                                                           suffix_name=suffix_name)  # , freq='daily'
            if stat_df is None:
                stat_df = stat_df_tmp
            else:
                stat_df = stat_df.merge(stat_df_tmp, how='outer', left_index=True, right_index=True)

            mdd_df = drawback_analysis(data_df)
            sheet_mdd_df_dic[sheet_name] = mdd_df
            sheet_mon_rr_dic[sheet_name] = mon_rr_dic
        except:
            logging.exception('处理 %s 时失败', sheet_name)
            continue
    return stat_df, sheet_mdd_df_dic, sheet_mon_rr_dic


def merge_nav(df_list, date_from=None):
    """
    合并 df_list 将净值进行合并
    :param df_list:
    :param date_from:
    :return:
    """
    nav_df = None
    for nav_tmp_df in df_list:
        if nav_df is None:
            nav_df = nav_tmp_df
        else:
            nav_df = nav_df.merge(nav_tmp_df, how='outer', right_index=True, left_index=True)
    # 净值拟合
    # def calc_mean(nav_s):
    #     nav_sub_s = nav_s.dropna()
    #     if nav_sub_s.shape[0] == 0:
    #         mean_val = np.nan
    #     else:
    #         mean_val = nav_sub_s.mean()
    #     return mean_val

    pct_df = nav_df.pct_change()
    pct_mean_s = pct_df.mean(axis=1).fillna(0) + 1
    # 进行日期过滤
    if date_from is not None:
        pct_mean_s = pct_mean_s[pct_mean_s.index >= str_2_date(date_from)]
    nav_merged_df = pd.DataFrame({"nav": pct_mean_s.cumprod()})
    stat_df, _ = return_risk_analysis(nav_merged_df, freq=None)
    stat_funds_df, _ = return_risk_analysis(nav_df, freq=None)
    stat_all_df = stat_df.merge(stat_funds_df, how='outer', right_index=True, left_index=True)
    return nav_merged_df, nav_df, stat_all_df


def merge_nav_from_file(file_list, date_from=None):
    """
    从excel或csv文件中读取历史净值数据，进行合并
    :param file_list:
    :param date_from:
    :return:
    """
    df_list = []
    error_dic = {}
    for file_info_dic in file_list:
        # 读取文件
        file_path = file_info_dic['file_path']
        file_path_no_extention, file_extension = os.path.splitext(file_path)
        try:
            if file_extension == '.csv':
                data_df = pd.read_csv(file_path)
            elif file_extension in ('.xls', '.xlsx'):
                data_df = pd.read_excel(file_path, index_col=0).reset_index()
            else:
                error_dic['file type'] = '不支持 %s 净值文件类型' % file_extension
        except:
            error_dic['file read'] = '文件内容读取失败'
            logging.exception('文件内容读取失败：%s', file_path_no_extention)
            continue
        # 设置索引
        if 'date_colum_name' in file_info_dic:
            date_colum_name = file_info_dic['date_colum_name']
            data_df.set_index(date_colum_name, inplace=True)
        else:
            date_colum_name = data_df.columns[0]
            data_df.set_index(date_colum_name, inplace=True)
        # 设置索引日期格式
        data_df.index = [try_2_date(x) for x in data_df.index]
        # 取nav数据
        if 'nav_colum_name_list' in file_info_dic:
            nav_colum_name_list = file_info_dic['nav_colum_name_list']
            if isinstance(nav_colum_name_list, list):
                nav_colum_name_dic = OrderedDict()
                for nav_column_name in nav_colum_name_list:
                    if isinstance(nav_column_name, str):
                        nav_colum_name_dic[nav_column_name] = nav_column_name
                    elif isinstance(nav_column_name, tuple):
                        nav_colum_name_dic[nav_column_name[0]] = nav_column_name[1]
                    else:
                        raise ValueError("%s 列名称无效" % nav_column_name)
                nav_df = data_df[list(nav_colum_name_dic.keys())].rename(columns=nav_colum_name_dic)
            else:
                nav_df = data_df[[nav_colum_name_list]]
        else:
            nav_df = data_df
        # 添加 df_list
        df_list.append(nav_df)
    # 合并
    nav_merged_df, nav_df, stat_df = merge_nav(df_list, date_from)
    return nav_merged_df, nav_df, stat_df


def create_instance(module_name, class_name, *args, **kwargs):
    """
    动态加载模块中的类，并实例化
    参见例子：src/fh_tools/language_test/base_test/dynamic_import_demo/dynamic_load.py
    :param module_name: 例如："src.fh_tools.language_test.base_test.dynamic_import_demo.a_class"
    :param class_name: 例如："AClass"
    :param args: "my_name" 类初始化参数
    :param kwargs:
    :return:
    """
    class_meta = load_class(module_name, class_name)
    obj = class_meta(*args, **kwargs)
    return obj


def load_class(module_name, class_name):
    """
    动态加载模块中的类
    参见例子：src/fh_tools/language_test/base_test/dynamic_import_demo/dynamic_load.py
    :param module_name: 例如："src.fh_tools.language_test.base_test.dynamic_import_demo.a_class"
    :param class_name: 例如："AClass"
    :return:
    """
    module_meta = __import__(module_name, globals(), locals(), [class_name])
    class_meta = getattr(module_meta, class_name)
    return class_meta


def decorator_timer(func):
    """
    为当期程序进行计时
    :param func:
    :return:
    """
    @functools.wraps(func)
    def timer_func(*args, **kwargs):
        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            end = time.time()
            estimate = time.strftime('%H:%M:%S', time.gmtime(end - start))
            logger.info('%s 运行时间：%s 相关参数 (%s, %s)', func.__name__, estimate, args, kwargs)

    return timer_func


def open_file_with_system_app(file_path, asyn=True):
    try:
        if platform.system() == 'Windows':
            os.startfile(file_path)
        elif platform.system() == 'Linux':
            import subprocess
            if asyn:
                subprocess.Popen(["xdg-open", file_path])
            else:
                subprocess.call(["xdg-open", file_path])
        else:
            import subprocess
            if asyn:
                subprocess.Popen(["open", file_path])
            else:
                subprocess.call(["open", file_path])
    except:
        import webbrowser
        webbrowser.open(f'file:///{file_path}')


def is_windows_os():
    return platform.system() == 'Windows'


def is_linux_os():
    return platform.system() == 'Linux'


def get_chinese_font_iter():
    fm = FontManager()
    mat_fonts = set(f.name for f in fm.ttflist)

    output = subprocess.check_output(
        'fc-list :lang=zh -f "%{family}\n"', shell=True)
    output = output.decode('utf-8')
    # print '*' * 10, '系统可用的中文字体', '*' * 10
    # print output
    zh_fonts = set(f.split(',', 1)[0] for f in output.split('\n'))
    available = mat_fonts & zh_fonts
    yield from available

    # print('*' * 10, '可用的字体', '*' * 10)
    # for num, f in enumerate(available, start=1):
    #     print(num, ')', f)


def get_project_root_path():
    import sys
    import os
    work_path = os.getcwd()
    # path_list = []
    # for path in sys.path:
    #     if work_path.find(path) == 0:
    #         print(path)
    #         path_list.append(path)
    path_list = list({_ for _ in sys.path if work_path.find(_) == 0})
    path_list.sort(key=len)
    project_root_path = path_list[0]
    return project_root_path, work_path


def get_module_path(stg_class: type):
    import os
    import sys
    module_path = stg_class.__module__
    if module_path == '__main__':
        project_root_path, work_path = get_project_root_path()
        # windows 环境下，sys.argv[0] 中路径分割为 "/" 而系统分隔符为 r"\" 导致匹配失败，因此需要进行一次转换
        module_file_path = os.path.splitext(sys.argv[0])[0].replace('/', os.path.sep)
        module_segment = [str(_) for _ in module_file_path[len(project_root_path):].split(os.path.sep) if _ != '']
        module_path = '.'.join(module_segment)
    return module_path


def counting_years(date_from_str, date_to_str):
    """
    用于计算两个日期之间相差多少年？返回float类型
    :param date_from_str:
    :param date_to_str:
    :return:
    """
    # date_from_str, date_to_str = '2018-05-01', '2019-05-31'
    date_from = str_2_date(date_from_str)
    date_to = str_2_date(date_to_str)

    year_start = str_2_date(f'{date_from.year}-01-01')
    year_end = str_2_date(f'{date_from.year}-12-31')
    ret_val1 = ((year_end - date_from).days + 1) / ((year_end - year_start).days + 1)

    year_start = str_2_date(f'{date_to.year}-01-01')
    year_end = str_2_date(f'{date_to.year}-12-31')
    ret_val2 = ((date_to - year_start).days + 1) / ((year_end - year_start).days + 1)

    ret_val = ret_val1 + ret_val2 + (date_to.year - date_from.year - 1)

    return ret_val


def get_module_file_path(stg_class: type):
    module_path = stg_class.__module__
    module = importlib.import_module(module_path)
    return module.__file__


def _test_get_module_file_path():
    # from ibats_common.example.tflearn.lstm3_stg import AIStg
    file_path = get_module_file_path(DataFrame)
    print(file_path)


def copy_module_file_to(module_str_or_class, folder_path):
    """将模板备份到指定目录下，不改变文件名"""
    if isinstance(module_str_or_class, str):
        module = importlib.import_module(module_str_or_class)
    # elif hasattr(module_str_or_class, '__module__'):
    #     module = importlib.import_module(module_str_or_class.__module__)
    elif isinstance(module_str_or_class, type):
        module = importlib.import_module(module_str_or_class.__module__)
    elif hasattr(module_str_or_class, '__file__'):
        module =module_str_or_class
    else:
        raise ValueError(f'{module_str_or_class} <{type(module_str_or_class)}> 不是有效的对象')

    file_path = module.__file__
    # _, file_name = os.path.split(file_path)
    # if not os.path.exists(folder_path):
    #     os.makedirs(folder_path)
    # new_file_path = os.path.join(folder_path, file_name)
    # shutil.copy(file_path, new_file_path)
    # return new_file_path
    return copy_file_to(file_path, folder_path)


def copy_file_to(file_path, folder_path):
    """将文件拷贝到指定目录"""
    _, file_name = os.path.split(file_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    new_file_path = os.path.join(folder_path, file_name)
    shutil.copy(file_path, new_file_path)
    return new_file_path


def _test_copy_module_file_to():
    copy_module_file_to(DataFrame, r'd:\Downloads')


def copy_folder_to(source_folder_path, target_folder_path):
    """将文件拷贝到指定目录，文件名不变"""
    _, folder_name = os.path.split(source_folder_path)
    new_folder_path = os.path.join(target_folder_path, folder_name)
    if os.path.exists(new_folder_path):
        shutil.rmtree(new_folder_path)
    shutil.copytree(source_folder_path, new_folder_path)
    return new_folder_path


def _test_copy_folder_to():
    folder_path = r'/home/mg/github/IBATS_Common/ibats_common/example/drl/d3qn1'
    copy_folder_to(folder_path, r'/home/mg/Downloads')


def sample_weighted(ll, weights, k):
    """
    带权重、非重复取样
    :param ll:
    :param weights:
    :param k:
    :return:
    """
    ll_len = len(ll)
    if ll_len < k:
        raise ValueError(f"len(ll)={ll_len}<{k}")
    elif ll_len == k:
        return random.sample(ll, k)
    else:
        new_ll = list(range(len(ll)))
        new_ll_set = set(new_ll)
        new_weights = np.array(weights)
        new_k = k
        result_tot = []
        while True:
            result = random.choices(new_ll, weights=new_weights[new_ll], k=new_k)
            result_set = set(result)
            result_tot.extend(result_set)
            new_ll_set -= result_set
            new_k = k - len(result_tot)
            new_ll = list(new_ll_set)
            if new_k == 0:
                break

        result_tot.sort()
        if isinstance(ll, np.ndarray):
            ret = ll[result_tot]
        else:
            ret = [ll[_] for _ in result_tot]
        return ret


def _test_weighted_sample():
    ll = list(range(1, 30))
    result = sample_weighted(ll, weights=ll, k=15)
    print(result)
    ll = np.eye(29)
    result = sample_weighted(ll, weights=np.arange(1, 30), k=15)
    print(result)


if __name__ == "__main__":
    pass
    # logging.basicConfig(level=logging.DEBUG,
    #   format='%(asctime)s %(name)s|%(funcName)s:%(lineno)d %(levelname)s %(message)s')
    # logger = logging.getLogger()
    # # 基金绩效分析
    # from pandas.io.formats.excel import ExcelCell
    # file_path = r'd:\WSPych\fof_ams\Stage\periodic_task\analysis_cache\2016-6-1_2018-6-1\各策略指数走势_按机构.csv'
    # file_path_no_extention, _ = os.path.splitext(file_path)
    # stat_df, sheet_mdd_df_dic, sheet_mon_rr_dic = return_risk_analysis_by_xls(
    #   file_path, encoding='GBK')  # , date_col="日期", nav_col_list=['产品净值']
    # if stat_df is not None:
    #     stat_df.to_csv('%s_绩效统计.csv' % file_path_no_extention, encoding='GBK')
    # for sheet_name, mdd_df in sheet_mdd_df_dic.items():
    #     mdd_df.to_csv('%s_%s_最大回撤.csv' % (file_path_no_extention, sheet_name), encoding='GBK')
    # if len(sheet_mon_rr_dic) > 0:
    #     xls_file_path = '%s_%s_月度收益.xls' % (file_path_no_extention, sheet_name)
    #     writer = pd.ExcelWriter(xls_file_path)
    #     try:
    #         for sheet_name, mon_rr_dic in sheet_mon_rr_dic.items():
    #             start_row = 1
    #             for name, monthly_rr_df in mon_rr_dic.items():
    #                 year_set = {trade_date.year for trade_date in monthly_rr_df.index}
    #                 monthly_rr_matrix_df = pd.DataFrame(index=year_set, columns=range(1, 13))
    #                 for trade_date, rr_s in monthly_rr_df.T.items():
    #                     monthly_rr_matrix_df.loc[trade_date.year, trade_date.month] = '%2.2f%%' % (rr_s[0] * 100)
    #                 # 写 excel
    #                 # sheet.write(start_row, 0, name)
    #                 writer.write_cells([ExcelCell(0, 0, name)], sheet_name, startrow=start_row - 1)
    #                 monthly_rr_matrix_df.to_excel(writer, sheet_name, startrow=start_row)
    #                 start_row += len(year_set) + 3
    #     finally:
    #         writer.close()

    # 基金净值合并
    # file_list = [
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\新萌\复华1号历史净值180105(1).xls"},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\新萌\历史净值171017.xls",
    #      'date_colum_name': '净值日期', 'nav_colum_name_list': ['最新净值']},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\新萌\新萌拟合后净值.xlsx",
    #      'date_colum_name': '日期', 'nav_colum_name_list': ['拟合后净值']},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\新萌\投放产品历史净值.csv",
    #      'date_colum_name': 'nav_date', 'nav_colum_name_list': ['nav_acc']},
    # ]

    # file_list = [
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\诚盛投资\诚盛2期Z期净值20171229nav.xlsx",
    #      'date_colum_name': '估值基准', 'nav_colum_name_list': [('单位净值',"诚盛2期Z期净值")]},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\诚盛投资\诚盛1期净值表.xlsx",
    #      'date_colum_name': '日期', 'nav_colum_name_list': ['诚盛1期净值']},
    # ]

    # file_list = [
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\合晟\合晟产品历史净值.csv"},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\展弘\展弘投放产品历史净值.xlsx"},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\新萌\新萌合并业绩后净值.xlsx"},
    #     {'file_path': r"d:\Works\F复华投资\L路演、访谈、评估报告\思勰\思勰合并后净值 2018 - 03 - 09.xls"},
    # ]
    #
    # file_list = [
    #     {'file_path': r'd:\Works\F复华投资\L路演、访谈、评估报告\思勰\思瑞二号周净值.xlsx',
    #      'date_colum_name': 'date', 'nav_colum_name_list': ['累计净值']},
    #     {'file_path': r'd:\Works\F复华投资\L路演、访谈、评估报告\思勰\2016.1-2016.10思勰净值.xlsx'},
    #     {'file_path': r'd:\Works\F复华投资\L路演、访谈、评估报告\思勰\思诚十二号周净值(1).xlsx',
    #      'date_colum_name': 'date', 'nav_colum_name_list': ['累计净值']},
    #     {'file_path': r'd:\Works\F复华投资\L路演、访谈、评估报告\思勰\SM2082-思瑞二号私募投资基金周净值(1).xls',
    #      'date_colum_name': '日期', 'nav_colum_name_list': ['累计净值']},
    # ]

    # nav_merged_df, nav_df, stat_df = merge_nav_from_file(file_list)
    # logging.info("\n%s", nav_merged_df)
    # logging.info("\n%s", nav_df)
    # logging.info("\n%s", stat_df)
    #
    # os.path.dirname(file_list[0]['file_path'])
    # folder_path = os.path.dirname(file_list[0]['file_path'])
    # file_name = "合并后净值.xls"
    # file_path = os.path.join(folder_path, file_name)
    # with pd.ExcelWriter(file_path) as writer:
    #     nav_merged_df.to_excel(writer, sheet_name="合并净值")
    #     nav_df.to_excel(writer, sheet_name="基金净值")
    #     stat_df.to_excel(writer, sheet_name="绩效统计")
    #     writer.save()
    # logging.info("输出文件：\n%s", file_path)

    # 测试 chuck 函数
    # a_list = list(range(1, 17))
    # for b_list in split_chunk(a_list, 4):
    #     print(b_list)
    # for b_list in split_chunk(a_list, 5):
    #     print(b_list)
    # for b_list in split_chunk(a_list, 16):
    #     print(b_list)
    # for b_list in split_chunk(a_list, 17):
    #     print(b_list)

    # 测试 log_param_when_exception 函数
    # @log_param_when_exception
    # def foo(a, b, c=None, *args, **kwargs):
    #     raise Exception('some error')
    #
    # foo(1, 2, 3, 4, e=5, f=6)

    # _test_get_module_file_path()
    # _test_copy_module_file_to()
    # _test_copy_folder_to()
    _test_get_idx_nb()
