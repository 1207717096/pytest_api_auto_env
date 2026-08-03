# -*- coding: utf-8 -*-
"""
@File    : allure_parser.py
@Time    : 2026/8/3 16:34
@Author  : @叶风磊
@Desc    : 
"""
import json
from pathlib import Path

class AllureParser:
    """Allure 报告解析器"""

    def __init__(self, report_path: str):
        self.report_path = Path(report_path)
        self.widgets_path = self.report_path / 'widgets'

    def get_summary(self) -> dict:
        """获取汇总数据"""
        summary_file = self.widgets_path / 'summary.json'
        if not self.report_path.exists():
            raise FileNotFoundError(
                f'❌ allure 报告目录不存在：{self.report_path}\n'
                f'   请先执行：allure generate ./allure-results -o {self.report_path} --clean'
            )
        if not summary_file.exists():
            raise FileNotFoundError(
                f'❌ 报告里缺关键文件：{summary_file}\n'
                f'   目录存在但结构异常，请重新生成 allure 报告。'
            )

        with open(summary_file, encoding='utf-8') as f:    # 顺手补上 utf-8 防中文乱码
            data = json.load(f)

        return {
            'total': data['statistic']['total'],
            'passed': data['statistic']['passed'],
            'failed': data['statistic']['failed'],
            'broken': data['statistic']['broken'],
            'skipped': data['statistic']['skipped'],
            'unknown': data['statistic']['unknown'],
            'duration_ms': data['time']['duration'],
            'start_time': data['time']['start'],
        }

    def get_failed_cases(self, limit: int = 5) -> list:
        """获取失败的用例"""
        summary_file = self.widgets_path / 'summary.json'
        if not summary_file.exists():
            return []    # 没数据就直接空，不抛异常

        with open(summary_file, encoding='utf-8') as f:
            data = json.load(f)

        failed = data.get('failed', [])[:limit]
        return [
            {
                'name': case['name'],
                'className': case.get('className', ''),
                'message': case.get('statusDetails', {}).get('message', ''),
            }
            for case in failed
        ]