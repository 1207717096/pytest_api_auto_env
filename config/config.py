# -*- coding: utf-8 -*-
"""
@File    : config.py
@Time    : 2026/7/21
@Author  : @叶风磊
@Desc    : 多环境配置加载器

环境选择优先级（从高到低）：
    1. 命令行参数：--env=xxx   例如：pytest --env=test
    2. 环境变量  ：TEST_ENV     例如：export TEST_ENV=prod
    3. DEFAULT_ENV 常量兜底

新增环境步骤：
    1) 在 config/environments/ 下新建一个 .py 文件（例如 staging.py）
    2) 在下方 ENV_REGISTRY 中追加 'staging': 'staging'
    3) 在该文件中定义与 dev.py 同名的所有变量即可
"""
import os
import sys
import logging


# ============ 全局默认值（与具体环境无关）============
DEFAULT_ENV = 'dev'
# 已注册的环境清单（新增/删除环境时，只改这里即可）
ENV_REGISTRY = {
    'dev': 'dev',
    'test': 'test',
    'prod': 'prod',
}


def _resolve_env_name():
    """根据 CLI / 环境变量 / 默认值 解析出当前使用的环境名"""
    # 1) 命令行参数 --env=xxx 或 --env xxx
    argv = sys.argv[1:]
    for i, arg in enumerate(argv):
        if arg.startswith('--env='):
            return arg.split('=', 1)[1].strip()
        if arg == '--env' and i + 1 < len(argv):
            return argv[i + 1].strip()
    # 2) 环境变量 TEST_ENV
    env_from_var = os.environ.get('TEST_ENV', '').strip()
    if env_from_var:
        return env_from_var
    # 3) 默认值
    return DEFAULT_ENV


def _load_env_module(env_name):
    """按环境名加载对应的配置模块"""
    if env_name not in ENV_REGISTRY:
        raise ValueError(
            f"未知的环境名：'{env_name}'。\n"
            f"已注册的环境：{list(ENV_REGISTRY.keys())}\n"
            f"请在 config/config.py 的 ENV_REGISTRY 中登记后重试，"
            f"或检查 --env 参数 / TEST_ENV 环境变量。"
        )
    module_name = ENV_REGISTRY[env_name]
    import importlib
    return importlib.import_module(f'config.environments.{module_name}')


# ============ 加载当前环境配置 ============
_CURRENT_ENV_NAME = _resolve_env_name()
_current_env = _load_env_module(_CURRENT_ENV_NAME)

# 把当前环境模块的所有「大写」变量提升到本命名空间
# 保持 `from config.config import *` 行为不变，向后兼容所有现有代码
_imported_vars = {
    name: getattr(_current_env, name)
    for name in dir(_current_env)
    if name.isupper() and not name.startswith('_')
}
globals().update(_imported_vars)

# 当前使用环境（用于日志 / 报告展示）
CURRENT_ENV = _CURRENT_ENV_NAME

logging.info(
    f"✅ 已加载环境配置：[{_CURRENT_ENV_NAME}] "
    f"{getattr(_current_env, 'ENV_DESC', '')} | BASE_URL={BASE_URL}"
)