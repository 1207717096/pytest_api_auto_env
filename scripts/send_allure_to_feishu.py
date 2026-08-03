# -*- coding: utf-8 -*-
"""
@File    : send_allure_to_feishu.py
@Time    : 2026/8/3 16:31
@Author  : @叶风磊
@Desc    : 
"""

# scripts/send_allure_to_feishu.py
import argparse
from allure_feishu_reporter import send_allure_report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='发送 Allure 报告到飞书')
    parser.add_argument('--webhook', required=True, help='飞书 Webhook URL')
    parser.add_argument('--secret', default='', help='签名密钥（可选）')
    parser.add_argument('--report-path', required=True, help='Allure 报告路径')
    parser.add_argument('--report-url', required=True, help='报告访问 URL')
    parser.add_argument('--at-all', action='store_true', help='@所有人')

    args = parser.parse_args()

    send_allure_report(
        webhook=args.webhook,
        secret=args.secret or None,
        allure_report_path=args.report_path,
        report_url=args.report_url,
        at_all=args.at_all,
    )