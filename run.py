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
    args = parser.parse_args()
    os.environ["TEST_ENV"] = args.env
    print(f"【run.py】本次执行环境: {args.env}")

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
        './testcase/test_runner_40.py',
        '--alluredir', allure_dir
    ])

    print(f"当前结果目录: {allure_dir}")
    print(f"历史备份目录: {history_dir}")
