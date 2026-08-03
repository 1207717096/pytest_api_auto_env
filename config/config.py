# -*- coding: utf-8 -*-
"""
@File    : config.py
@Time    : 2026/7/14 18:53
@Author  : @叶风磊
@Desc    : 配置信息
"""

import os
import sys

print(f"【config.py】文件路径: {os.path.abspath(__file__)}")
print(f"【config.py】Python 解释器: {sys.executable}")
print(f"【config.py】TEST_ENV 原始值: {os.getenv('TEST_ENV', '未设置')}")

# 默认环境（与 Jenkins shell 脚本兜底值保持一致）
ENV = os.getenv("TEST_ENV", "dev")

# 多环境配置
config = {
    "dev": {
        #环境基准地址：
        "BASE_URL" : 'http://127.0.0.1:8888/api/private/v1/dev',
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
        "BASE_URL" : 'http://127.0.0.1:8888/api/private/v1/test',
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
        "BASE_URL" : 'http://127.0.0.1:8888/api/private/v1/pre',
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
        "BASE_URL" : 'http://127.0.0.1:8888/api/private/v1/prod',
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

if ENV not in config:
    raise ValueError(f"未知环境 TEST_ENV={ENV!r}，可选值: {list(config.keys())}")

# 当前选中环境的配置
current = config[ENV]

# 展开为模块级变量，兼容 `from config.config import *`（BASE_URL / EXCEL_FILE 等）
globals().update(current)

# ============================================================
# ★ 运行时覆盖：允许通过环境变量 / Jenkins Choice 参数切换 Excel 文件
#   优先级：CLI 参数（run.py 已写入 env） > 环境变量 > 环境配置中的默认值
#   同时更新 current 字典 与 模块顶层变量，让两种引用风格都生效
# ============================================================
_overrides = {
    'EXCEL_FILE': os.environ.get('TEST_EXCEL_FILE', '').strip(),
    'SHEET_NAME': os.environ.get('TEST_SHEET_NAME', '').strip(),
}
for _key, _val in _overrides.items():
    if _val:
        current[_key] = _val          # 影响 `from config.config import current` 的代码
        globals()[_key] = _val         # 影响 `from config.config import *` 的代码
        print(f'【Excel 覆盖】{_key} = {_val}  (来源：环境变量)')

print(f"【环境校验】读取到的 TEST_ENV 变量值：{ENV}")
print(f"【环境校验】当前环境BASE_URL：{BASE_URL}")
print(f"【环境校验】当前 Excel 文件：{EXCEL_FILE} (sheet={SHEET_NAME})")
