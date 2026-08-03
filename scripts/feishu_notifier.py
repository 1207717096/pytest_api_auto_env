# -*- coding: utf-8 -*-
"""
@File    : feishu_notifier.py
@Time    : 2026/8/3 16:32
@Author  : @叶风磊
@Desc    : 
"""
# feishu_notifier.py
import time
import hmac
import hashlib
import base64
import json
import requests
from typing import Optional

class FeishuNotifier:
    """飞书消息推送器"""

    def __init__(self, webhook: str, secret: Optional[str] = None):
        """
        :param webhook: 飞书机器人 webhook URL
        :param secret: 签名校验密钥（启用签名校验时必填）
        """
        self.webhook = webhook
        self.secret = secret

    def _gen_sign(self, timestamp: str) -> str:
        """生成签名（启用签名校验时使用）"""
        string_to_sign = f'{timestamp}\n{self.secret}'
        hmac_code = hmac.new(
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256,
        ).digest()
        return base64.b64encode(hmac_code).decode('utf-8')

    def send_text(self, text: str, at_all: bool = False) -> dict:
        """发送简单文本消息"""
        payload = {
            'msg_type': 'text',
            'content': {'text': text},
        }
        if at_all:
            payload['content']['text'] += ' <at user_id="all">所有人</at>'

        return self._send(payload)

    def send_rich_text(self, title: str, content: list) -> dict:
        """
        发送富文本消息
        :param content: [[{"tag": "text", "text": "..."}, ...], ...]
        """
        payload = {
            'msg_type': 'post',
            'content': {
                'post': {
                    'zh_cn': {
                        'title': title,
                        'content': content,
                    }
                }
            },
        }
        return self._send(payload)

    def send_card(
        self,
        title: str,
        elements: list,
        header_color: str = 'blue',
        card_link: Optional[str] = None,
    ) -> dict:
        """
        发送交互式卡片（推荐）
        :param header_color: blue / green / red / orange / grey
        """
        card = {
            'config': {'wide_screen_mode': True},
            'header': {
                'title': {'tag': 'plain_text', 'content': title},
                'template': header_color,
            },
            'elements': elements,
        }
        if card_link:
            card['card_link'] = {'url': card_link}

        payload = {
            'msg_type': 'interactive',
            'card': card,
        }
        return self._send(payload)

    def _send(self, payload: dict) -> dict:
        """底层发送逻辑"""
        if self.secret:
            timestamp = str(int(time.time()))
            payload['timestamp'] = timestamp
            payload['sign'] = self._gen_sign(timestamp)

        resp = requests.post(self.webhook, json=payload, timeout=10)
        return resp.json()