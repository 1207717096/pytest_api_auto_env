# -*- coding: utf-8 -*-
"""
@File    : db_assert.py
@Time    : 2026/8/19
@Author  : @叶风磊
@Desc    : JSON 嵌入式数据库断言解析器

Excel 用例中 `db_assert` 字段格式（方案 C：JSON 嵌入）：

[
  {
    "sql": "SELECT age, name FROM user WHERE id=1",
    "assert": [
      {"field": "age",  "type": "eq",       "value": 25},
      {"field": "name", "type": "contains", "value": "zhang"}
    ]
  },
  {
    "sql": "SELECT count(*) AS cnt FROM user WHERE status=1",
    "assert": [
      {"field": "cnt", "type": "gt", "value": 0}
    ]
  }
]

支持的断言类型（type）：
- eq          : 实际 == 期望
- ne          : 实际 != 期望
- gt          : 实际 >  期望
- ge          : 实际 >= 期望
- lt          : 实际 <  期望
- le          : 实际 <= 期望
- in          : 期望 是字符串或列表，实际 in 期望（或 期望 in 实际，字符串场景）
- contains    : 字符串包含（实际 包含 期望）
- not_contains: 字符串不包含
- is_null     : 实际为 None
- is_not_null : 实际不为 None
"""
import json
import logging

import allure

from utils.send_request import send_jdbc_request_dict


# 断言类型与对应比较函数映射
# op_func(actual, expected) -> bool
_ASSERT_OPS = {
    'eq': lambda a, e: a == e,
    'ne': lambda a, e: a != e,
    'gt': lambda a, e: a is not None and a > e,
    'ge': lambda a, e: a is not None and a >= e,
    'lt': lambda a, e: a is not None and a < e,
    'le': lambda a, e: a is not None and a <= e,
    'contains': lambda a, e: e is not None and e in (a or ''),
    'not_contains': lambda a, e: e is not None and e not in (a or ''),
    'is_null': lambda a, e: a is None,
    'is_not_null': lambda a, e: a is not None,
}


def _coerce(value):
    """
    数字字符串尽量转成数字，方便 `gt/ge/lt/le` 等数值比较。
    JSON 里手写 `25` 已经是 int，但 Excel 解析时经常被读成字符串。
    """
    if isinstance(value, (int, float, bool)):
        return value
    if isinstance(value, str):
        s = value.strip()
        if s == '':
            return value
        try:
            if '.' in s:
                return float(s)
            return int(s)
        except ValueError:
            return value
    return value


def _eval_one(actual, op, expected):
    """执行单条断言；不通过直接抛 AssertionError。"""
    op_func = _ASSERT_OPS.get(op)
    if op_func is None:
        raise AssertionError(f'不支持的断言类型 type={op!r}，可选：{list(_ASSERT_OPS.keys())}')

    # 数值型断言前先做一次类型适配，避免 Excel 把所有字段读成字符串
    if op in ('gt', 'ge', 'lt', 'le', 'eq', 'ne'):
        if not isinstance(expected, (bool, type(None))):
            expected = _coerce(expected)
        actual = _coerce(actual)

    if op == 'is_null' or op == 'is_not_null':
        ok = op_func(actual, expected)
    else:
        ok = op_func(actual, expected)

    if not ok:
        raise AssertionError(
            f'数据库断言失败：type={op}, field={actual!r}, expected={expected!r}'
        )


def _parse_db_assert(raw):
    """
    解析 Excel 单元格里的 db_assert。
    支持以下形式：
    1) JSON 字符串 -> list[dict]
    2) Python 字面量（dict / list）字符串 -> list[dict]
    3) 已为 list / dict -> 直接返回
    4) 空 / None -> []
    """
    if raw is None or raw == '':
        return []
    if isinstance(raw, (list, dict)):
        data = raw
    else:
        text = str(raw).strip()
        if not text:
            return []
        # 优先尝试 JSON，失败再回退 eval
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = eval(text)  # noqa: S307 - 用例由测试人员维护
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise AssertionError(f'db_assert 格式错误，期望 list[dict]，实际 {type(data).__name__}')
    return data


@allure.step('3、数据库断言（JSON 嵌入式）')
def db_assert(raw_db_assert):
    """
    执行 JSON 嵌入式数据库断言。

    :param raw_db_assert: Excel 单元格中的 db_assert 内容
    """
    groups = _parse_db_assert(raw_db_assert)
    if not groups:
        return

    for idx, group in enumerate(groups, start=1):
        sql = group.get('sql')
        asserts = group.get('assert', [])
        if not sql:
            raise AssertionError(f'db_assert 第 {idx} 组缺少 sql 字段：{group}')
        if not isinstance(asserts, list) or not asserts:
            raise AssertionError(f'db_assert 第 {idx} 组缺少 assert 列表：{group}')

        row = send_jdbc_request_dict(sql)
        logging.info(f'3.数据库断言 SQL={sql} 实际结果={row}')

        if not row:
            # 数据库无数据：除 is_null/is_not_null 之外都会失败
            for one in asserts:
                op = one.get('type', 'eq')
                if op == 'is_null':
                    continue
                raise AssertionError(
                    f'数据库断言失败：SQL={sql} 无返回数据，且 type={op} 不允许为空'
                )

        for one in asserts:
            field = one.get('field')
            op = one.get('type', 'eq')
            expected = one.get('value')
            if field is None and op not in ('is_null', 'is_not_null'):
                raise AssertionError(f'db_assert 断言项缺少 field：{one}')

            actual = row.get(field)
            logging.info(f'3.数据库断言 -> {op}({field}: 实际={actual!r}, 期望={expected!r})')
            _eval_one(actual, op, expected)
