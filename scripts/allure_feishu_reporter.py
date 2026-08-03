# -*- coding: utf-8 -*-
"""
@File    : allure_feishu_reporter.py
@Time    : 2026/8/3 16:32
@Author  : @叶风磊
@Desc    : 
"""
# allure_feishu_reporter.py
from pathlib import Path
from feishu_notifier import FeishuNotifier
from allure_parser import AllureParser

def seconds_to_readable(ms: int) -> str:
    """毫秒转可读格式"""
    seconds = ms / 1000
    if seconds < 60:
        return f'{seconds:.1f} 秒'
    elif seconds < 3600:
        return f'{seconds / 60:.1f} 分'
    else:
        return f'{seconds / 3600:.1f} 小时'

def build_allure_card(report_url: str, allure_report_path: str) -> dict:
    """构造 Allure 卡片消息"""
    parser = AllureParser(allure_report_path)
    summary = parser.get_summary()           # 这里如果文件不存在，会抛 FileNotFoundError 自带详细提示
    failed_cases = parser.get_failed_cases(limit=5)
    if not summary.get('total', 0):
        raise ValueError(
            f'❌ Allure 报告数据为空或全为 0：{allure_report_path}\n'
            f'   请确认 pytest 真的跑过、有用例被执行。'
        )

    total = summary['total']
    passed = summary['passed']
    failed = summary['failed']
    broken = summary['broken']
    skipped = summary['skipped']
    duration = seconds_to_readable(summary['duration_ms'])

    # 计算通过率
    pass_rate = passed / total * 100 if total > 0 else 0

    # 决定头部颜色
    if failed > 0 or broken > 0:
        header_color = 'red'
        title = f'❌ 测试执行失败（{passed}/{total}）'
    elif pass_rate < 90:
        header_color = 'orange'
        title = f'⚠️ 测试部分失败（{passed}/{total}）'
    else:
        header_color = 'green'
        title = f'✅ 测试全部通过（{passed}/{total}）'

    # 卡片元素
    elements = [
        # 第一行：核心数据
        {
            'tag': 'div',
            'fields': [
                {'is_short': True, 'text': {
                    'tag': 'lark_md',
                    'content': f'**📊 总用例数**\n{total}'
                }},
                {'is_short': True, 'text': {
                    'tag': 'lark_md',
                    'content': f'**✅ 通过数**\n{passed}'
                }},
                {'is_short': True, 'text': {
                    'tag': 'lark_md',
                    'content': f'**❌ 失败数**\n{failed}'
                }},
            ],
        },
        {
            'tag': 'div',
            'fields': [
                {'is_short': True, 'text': {
                    'tag': 'lark_md',
                    'content': f'**⚠️ 异常数**\n{broken}'
                }},
                {'is_short': True, 'text': {
                    'tag': 'lark_md',
                    'content': f'**⏭ 跳过数**\n{skipped}'
                }},
                {'is_short': True, 'text': {
                    'tag': 'lark_md',
                    'content': f'**⏱ 耗时**\n{duration}'
                }},
            ],
        },
        # 分隔线
        {'tag': 'hr'},
        # 失败用例详情
    ]

    if failed_cases:
        elements.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': f'**❌ 失败用例 Top {len(failed_cases)}：**\n' + '\n'.join([
                    f'• `{case["name"]}`' +
                    (f'\n   错误：{case["message"][:100]}' if case['message'] else '')
                    for case in failed_cases
                ]),
            },
        })
    else:
        elements.append({
            'tag': 'div',
            'text': {
                'tag': 'lark_md',
                'content': '🎉 所有用例执行成功，无失败项',
            },
        })

    # 通过率（用文本进度条，避免 progress block 不被服务端识别）
    bar_len = 20
    filled = int(round(pass_rate / 100 * bar_len))
    bar = '▓' * filled + '░' * (bar_len - filled)
    elements.append({
        'tag': 'div',
        'text': {
            'tag': 'lark_md',
            'content': f'**通过率** `{bar}` **{pass_rate:.2f}%**',
        },
    })

    # 注释
    elements.append({
        'tag': 'note',
        'elements': [
            {'tag': 'plain_text', 'content': f'通过率：{pass_rate:.2f}%'}
        ],
    })

    # 按钮
    elements.append({
        'tag': 'action',
        'actions': [
            {
                'tag': 'button',
                'text': {'tag': 'plain_text', 'content': '📊 查看完整报告'},
                'type': 'primary',
                'url': report_url,
            },
            {
                'tag': 'button',
                'text': {'tag': 'plain_text', 'content': '🔗 Jenkins Job'},
                'type': 'default',
                'url': report_url.rsplit('/allure', 1)[0],
            },
        ],
    })

    return {
        'title': title,
        'elements': elements,
        'header_color': header_color,
        'card_link': report_url,
    }

def send_allure_report(
    webhook: str,
    secret: str,
    allure_report_path: str,
    report_url: str,
    at_all: bool = False,
):
    """主入口：推送 Allure 报告到飞书"""
    notifier = FeishuNotifier(webhook, secret)

    card = build_allure_card(report_url, allure_report_path)

    result = notifier.send_card(
        title=card['title'],
        elements=card['elements'],
        header_color=card['header_color'],
        card_link=card['card_link'],
    )

    if result.get('StatusCode') == 0 or result.get('code') == 0:
        print('✅ 飞书消息推送成功')
    else:
        print(f'❌ 推送失败：{result}')

# ============ 使用示例 ============
if __name__ == '__main__':
    send_allure_report(
        webhook='https://open.feishu.cn/open-apis/bot/v2/hook/xxx',
        secret='SECxxx',                  # 可选
        allure_report_path='reports/allure-report',
        report_url='http://jenkins.example.com/job/my-job/allure',
        at_all=False,
    )