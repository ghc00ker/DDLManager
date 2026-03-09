"""QQ 聊天记录解析器"""
from datetime import datetime
import json
from typing import List
from .base import MessageParser
from ..models import Message


class QQParser(MessageParser):
    """解析 QQ 导出的聊天记录 JSON 文件"""
    
    def parse(self, source) -> List[Message]:
        """解析 QQ 导出文件
        
        Args:
            source: 文件路径（str）或已加载的字典（dict）
        """
        
        with open(source, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        raw_messages = data.get('messages', []) # 如果messages不存在返回空
        messages = []
        
        for raw_msg in raw_messages:
            try:
                msg = self.from_qq_export(raw_msg)
                messages.append(msg)
            except Exception as e:
                print(f"警告：跳过无效消息 {raw_msg.get('id')}: {e}")
                continue
        
        return messages
    
    @classmethod
    def extract_text_from_content(cls, content: dict) -> str:
        """从 QQ content 结构中提取纯文本
        
        为什么要单独提取？
        - QQ 消息可能包含 @、表情、文件等复杂结构
        - 统一转为纯文本方便后续 AI 处理
        """
        if not content:
            return ''
        
        text = content.get('text')
        if text and str(text).strip():
            return str(text).strip()
        
        parts = []
        elements = content.get('elements') or []
        for el in elements:
            t = el.get('type')
            data = el.get('data') or {}
            if t == 'text':
                parts.append(str(data.get('text') or ''))
            elif t == 'at':
                parts.append('@' + str(data.get('name') or data.get('uid') or ''))
            elif t == 'face':
                parts.append('[' + str(data.get('name') or '表情') + ']')
            elif t == 'file':
                parts.append('[文件: ' + str(data.get('filename') or '') + ']')
            elif t == 'image':
                parts.append('[图片]')
        
        return ''.join(parts).strip()
    
    @classmethod
    def from_qq_export(cls, raw_message: dict) -> 'Message':
        """从 QQ 导出的 JSON 格式创建消息对象"""
        mid = raw_message.get('id', '')
        ts = datetime.fromtimestamp(raw_message.get('timestamp') / 1000)
        sender = raw_message.get('sender') or {}
        sender_name = sender.get('name') or sender.get('uid') or ''
        sender_uid = sender.get('uid')
        content = raw_message.get('content') or {}
        text = QQParser.extract_text_from_content(content)
        
        return Message(mid, sender_name, sender_uid, text, ts)
    
