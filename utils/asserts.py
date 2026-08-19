# -*- coding: utf-8 -*-
"""
@File    : asserts.py
@Time    : 2026/7/14 18:18
@Author  : @叶风磊
@Desc    : 断言文件的封装：http断言 + 数据库断言
"""
import jsonpath
import allure
import logging

from utils.send_request import send_jdbc_request
from utils.db_assert import db_assert as _db_assert_json


@allure.step('3、HTTP响应断言')
def http_assert(case, res, index=0):
    if case['check']:
        result = jsonpath.jsonpath(res.json(), case['check'])[index]
        logging.info(f'3.http响应断言的内容是：实际结果（ {result} ）== 预期结果（ {case["expected"]}）')
        assert result == case["expected"]
    else:
        logging.info(f'3.http响应断言的内容是：预期结果（ {case["expected"]} ）in 实际结果（ {res.text}）')
        assert case["expected"] in res.text


def jdbc_assert(case):
    """
    数据库断言入口：
    - 优先使用 JSON 嵌入式 db_assert（方案 C，最灵活）
    - 兼容旧版 sql_check + sql_expected
    """
    raw_db_assert = case.get('db_assert')

    # 1) 方案 C：JSON 嵌入式数据库断言
    if raw_db_assert not in (None, ''):
        _db_assert_json(raw_db_assert)
        return

    # 2) 兼容旧用法：sql_check + sql_expected
    if case.get('sql_check') and case.get('sql_expected'):
        with allure.step('3.JDBC响应断言'):
            result = send_jdbc_request(case['sql_check'])
            logging.info(f'3.jdbc响应断言的内容：实际结果（ {result} ）== 预期结果（ {case["sql_expected"]}）')
            assert result == case['sql_expected']
