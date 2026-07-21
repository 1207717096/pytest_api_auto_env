# -*- coding: utf-8 -*-
"""
@File    : config.py
@Time    : 2026/7/14 18:53
@Author  : @叶风磊
@Desc    : 配置信息
"""

import os

# 默认环境
ENV = os.getenv("TEST_ENV", "test")

# 多环境配置
config = {
    "dev": {
        #环境基准地址：
        "BASE_URL" : 'http://127.0.0.1:8888/api/private/v1',
        #excel格式的测试用例文件配置
        "EXCEL_FILE" :'./data/测试用例.xlsx',
        "SHEET_NAME" : 'Sheet1',
        #mysql 配置信息,
        "DB_HOST" : '127.0.0.1',
        "DB_USER" : 'root',
        "DB_PASSWORD" : '123456',
        "DB_NAME" : 'mydb',
        "DB_PORT" : 3306
    },
    "test": {
        #环境基准地址：
        "BASE_URL" : 'http://127.0.0.1:8888/api/private/v1',
        #excel格式的测试用例文件配置
        "EXCEL_FILE" :'./data/测试用例.xlsx',
        "SHEET_NAME" : 'Sheet1',
        #mysql 配置信息,
        "DB_HOST" : '127.0.0.1',
        "DB_USER" : 'root',
        "DB_PASSWORD" : '123456',
        "DB_NAME" : 'mydb',
        "DB_PORT" : 3306
    },
    "pre": {
        #环境基准地址：
        "BASE_URL" : 'http://127.0.0.1:8888/api/private/v1',
        #excel格式的测试用例文件配置
        "EXCEL_FILE" :'./data/测试用例.xlsx',
        "SHEET_NAME" : 'Sheet1',
        #mysql 配置信息,
        "DB_HOST" : '127.0.0.1',
        "DB_USER" : 'root',
        "DB_PASSWORD" : '123456',
        "DB_NAME" : 'mydb',
        "DB_PORT" : 3306
    },
    "prod": {
        #环境基准地址：
        "BASE_URL" : 'http://127.0.0.1:8888/api/private/v1',
        #excel格式的测试用例文件配置
        "EXCEL_FILE" :'./data/测试用例.xlsx',
        "SHEET_NAME" : 'Sheet1',
        #mysql 配置信息,
        "DB_HOST" : '127.0.0.1',
        "DB_USER" : 'root',
        "DB_PASSWORD" : '123456',
        "DB_NAME" : 'mydb',
        "DB_PORT" : 3306
    }
}