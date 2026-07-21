# -*- coding: utf-8 -*-
"""
@File    : dev.py
@Time    : 2026/7/21
@Author  : @叶风磊
@Desc    : 开发环境（dev）配置
"""
# 环境基准地址
BASE_URL = 'http://127.0.0.1:8888/api/private/v1'

# Excel 测试用例配置
EXCEL_FILE = './data/测试用例.xlsx'
SHEET_NAME = 'Sheet1'

# MySQL 配置
DB_HOST = '127.0.0.1'
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_NAME = 'mydb'
DB_PORT = 3306

# 环境描述（仅用于日志/报告展示）
ENV_NAME = 'dev'
ENV_DESC = '本地开发环境'