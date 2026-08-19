# -*- coding: utf-8 -*-
"""
@File    : send_request.py
@Time    : 2026/7/14 17:41
@Author  : @叶风磊
@Desc    : 发送请求的方法封装
"""
import pymysql
import requests
import allure
import logging
from config.config import current


@allure.step('2、发送HTTP请求')
def send_http_request(**request_data):
    logging.info(f'2.发送http请求，响应“{requests.request(**request_data).text}')
    return requests.request(**request_data)


def _get_connection():
    """建立 MySQL 连接，每次调用重新建立，避免长连接导致的超时问题。"""
    return pymysql.Connect(
        host=current['DB_HOST'],
        user=current['DB_USER'],
        password=current['DB_PASSWORD'],
        database=current['DB_NAME'],
        charset='utf8',
        port=current['DB_PORT']
    )


def send_jdbc_request(sql, index=0):
    """
    兼容旧用法：返回单行单列的值（按 index 取第几列）。

    备注：
    - 旧框架很多地方用 `send_jdbc_request(sql)` / `send_jdbc_request(sql, 0)` 拿一个标量。
    - 新的 JSON 嵌入式数据库断言会调用 `send_jdbc_request_dict` 拿整行字典。
    """
    sq = _get_connection()
    try:
        cur = sq.cursor()
        cur.execute(sql)
        result = cur.fetchone()
    finally:
        try:
            cur.close()
        except Exception:
            pass
        sq.close()
    return result[index]


def send_jdbc_request_dict(sql):
    """
    执行 SQL 并返回 `{列名: 值}` 的字典。

    主要服务 JSON 嵌入式数据库断言：
    - 断言中通过 `field` 指定列名，避免依赖列顺序。
    - 当 SQL 返回多行时仅取第一行。
    """
    sq = _get_connection()
    try:
        cur = sq.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
    finally:
        try:
            cur.close()
        except Exception:
            pass
        sq.close()

    if not rows:
        return {}
    return rows[0]
