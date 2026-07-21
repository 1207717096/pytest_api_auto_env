# -*- coding: utf-8 -*-
"""
@File    : analyse_case.py
@Time    : 2026/7/14 17:29
@Author  : @叶风磊
@Desc    : 解析测试用例
"""
import logging

import allure
from config.config import current

@allure.step('1、解析请求数据')
def analyse_case(case):

    method = case['method']
    url = current['BASE_URL'] + case['path']
    headers = eval(case['headers']) if isinstance(case['headers'], str) else None
    params = eval(case['params']) if isinstance(case['params'], str) else None
    data = eval(case["data"]) if isinstance(case["data"], str) else None
    json = eval(case['json']) if isinstance(case['json'], str) else None
    files = eval(case['files']) if isinstance(case['files'], str) else None

    request_data = {
        'method': method,
        'url': url,
        'headers': headers,
        'params': params,
        'data': data,
        'json': json,
        'files': files
    }
    logging.info(f'1.解析请求数据，请求数据为：{request_data}')
    allure.attach(f'1.解析请求数据，请求数据为：{request_data}')
    #需要加上返回值
    return request_data