import argparse
import os
import shutil
import sys
from datetime import datetime


def parse_args():
    """解析运行参数"""
    parser = argparse.ArgumentParser(description='接口自动化测试一键执行入口')
    # 用例脚本路径（默认最新版本）
    parser.add_argument(
        '--case',
        default='./testcase/test_runner_40.py',
        help='要执行的测试脚本路径，默认 ./testcase/test_runner_40.py',
    )
    # 环境选择（透传给 pytest / config.config）
    parser.add_argument(
        '--env',
        default=None,
        help='要执行的环境，例如 dev / test / prod。'
             '留空时回退到 TEST_ENV 环境变量或 config 默认值。',
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    # ★ 在 import pytest 之前先把 --env 注入到 sys.argv，
    #   保证 config.config 能正确解析环境（也可只通过 TEST_ENV 注入）
    if args.env and '--env' not in sys.argv:
        sys.argv.append(f'--env={args.env}')
        # 同时导出环境变量，让子进程（pytest 插件/Allure 等）也能感知
        os.environ['TEST_ENV'] = args.env

    # 在 import pytest 之前 import config，让环境日志尽早打出
    from config.config import CURRENT_ENV, BASE_URL  # noqa: F401

    import pytest

    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

    # 固定路径（Jenkins Allure 插件读取）
    allure_dir = os.path.join(PROJECT_DIR, "allure-results")

    # 历史备份目录
    history_dir = os.path.join(PROJECT_DIR, "allure-history")
    os.makedirs(history_dir, exist_ok=True)

    # 如果已有结果，备份到历史目录
    if os.path.exists(allure_dir) and os.listdir(allure_dir):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(history_dir, f"report_{timestamp}")
        shutil.copytree(allure_dir, backup_dir)
        print(f"历史结果已备份到: {backup_dir}")

        # 清理旧结果
        shutil.rmtree(allure_dir)

    # 创建新的 allure-results 目录
    os.makedirs(allure_dir)

    # 运行测试，生成 allure 结果
    pytest.main([
        '-vs',
        args.case,
        '--alluredir', allure_dir,
    ])

    print(f"当前结果目录: {allure_dir}")
    print(f"历史备份目录: {history_dir}")
    print(f"本次执行环境: [{CURRENT_ENV}] | BASE_URL={BASE_URL}")