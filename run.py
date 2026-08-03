import argparse
import pytest
import os
import shutil
from datetime import datetime

if __name__ == '__main__':
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

    # 解析 --env，并写入环境变量（须在 pytest 加载 config 之前完成）
    parser = argparse.ArgumentParser(description="接口自动化测试入口")
    parser.add_argument(
        "--env",
        default=os.getenv("TEST_ENV", "dev"),
        choices=["dev", "test", "pre", "prod"],
        help="指定测试环境，对应 config.py 中的 key",
    )
    parser.add_argument(
        "--excel-file",
        default=None,
        help="指定本次要跑的 Excel 测试用例文件，例如 ./data/smoke_cases.xlsx。"
             "留空则使用环境配置 / 环境变量 TEST_EXCEL_FILE 中的默认值。",
    )
    parser.add_argument(
        "--sheet-name",
        default=None,
        help="Excel 中的 sheet 名（仅切换 Excel 时可一并指定）。",
    )
    parser.add_argument(
        "--case",
        default="./testcase/test_runner_40.py",
        help="要执行的 pytest 用例脚本，默认最新版本。",
    )
    args = parser.parse_args()

    # 把 env / excel / sheet 全部写到环境变量，保证 config.py 能读到
    os.environ["TEST_ENV"] = args.env
    if args.excel_file:
        os.environ["TEST_EXCEL_FILE"] = args.excel_file
    if args.sheet_name:
        os.environ["TEST_SHEET_NAME"] = args.sheet_name

    print(f"【run.py】本次执行环境: {args.env}")
    print(f"【run.py】本次 Excel 文件: {args.excel_file or os.getenv('TEST_EXCEL_FILE', '<使用配置默认值>')}")
    print(f"【run.py】本次 Sheet 名:    {args.sheet_name or os.getenv('TEST_SHEET_NAME', '<使用配置默认值>')}")

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
    
    # 创建新的 allure-results 目录（exist_ok=True 兼容目录已存在但为空的情况）
    os.makedirs(allure_dir, exist_ok=True)

    # 运行测试，生成 allure 结果
    pytest.main([
        '-vs',
        args.case,
        '--alluredir', allure_dir
    ])

    print(f"当前结果目录: {allure_dir}")
    print(f"历史备份目录: {history_dir}")
