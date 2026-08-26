# -*- coding: utf-8 -*-
"""
@File    : excel_utils.py
@Time    : 2026/7/12 15:55
@Author  : @叶风磊
@Desc    : 读取和操作excel文件的工具
"""

import os

import openpyxl
from config.config import EXCEL_FILE, SHEET_NAME


# 项目根目录：本文件所在 utils/ 的上一级
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve_path(path):
    """
    把相对路径解析成以项目根目录为基准的绝对路径。
    - 绝对路径直接返回
    - 相对路径基于 PROJECT_ROOT（与运行时的 cwd 解耦）
    """
    if os.path.isabs(path):
        return path
    return os.path.join(PROJECT_ROOT, path)


def read_excel(file_path=EXCEL_FILE, sheet_name=SHEET_NAME):
    """
    读取 Excel 用例。
    - file_path: 相对项目根的路径（默认取 config 中的 EXCEL_FILE）
    - sheet_name: Sheet 名
    """
    abs_path = _resolve_path(file_path)

    workbook = openpyxl.load_workbook(abs_path)
    worksheet = workbook[sheet_name]

    data = []
    keys = [cell.value for cell in worksheet[2]]      # 第 2 行：表头
    for row in worksheet.iter_rows(min_row=3, values_only=True):
        dict_data = dict(zip(keys, row))
        if dict_data.get("is_True"):
            data.append(dict_data)

    workbook.close()
    return data
