#! /usr/bin/env python
# -*- coding:utf-8 -*-
"""
@author  : MG
@Time    : 19-4-9 上午9:47
@File    : test_db.py
@contact : mmmaaaggg@163.com
@desc    : 
"""
import unittest
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from ibats_utils.db import bunch_insert_on_duplicate_update


class SomeTest(unittest.TestCase):  # 继承unittest.TestCase

    def test_func(self):
        engine = create_engine("mysql://mg:Dcba1234@localhost/md_integration?charset=utf8",
                               echo=False, encoding="utf-8")
        table_name = 'test_only'
        # if not engine.has_table(table_name):
        #     df = pd.DataFrame({'a': [1.0, 11.0], 'b': [2.0, 22.0], 'c': [3, 33], 'd': [4, 44]})
        #     df.to_sql(table_name, engine, index=False, if_exists='append')
        #     with with_db_session(engine) as session:
        #         session.execute("""ALTER TABLE {table_name}
        #     CHANGE COLUMN a a DOUBLE NOT NULL FIRST,
        #     CHANGE COLUMN d d INTEGER,
        #     ADD PRIMARY KEY (a)""".format(table_name=table_name))

        df = pd.DataFrame({'a': [1.0, 111.0], 'b': [2.2, 222.0], 'c': [np.nan, np.nan]})
        insert_count = bunch_insert_on_duplicate_update(
            df, table_name, engine, dtype=None, myisam_if_create_table=True,
            primary_keys=['a', 'b'], schema='md_integration')
        self.assertEqual(insert_count, 2)


if __name__ == '__main__':
    unittest.main()  # 运行所有的测试用例
