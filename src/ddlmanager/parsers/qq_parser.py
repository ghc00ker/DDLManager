"""QQ 聊天记录解析器"""
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
        if isinstance(source, str):
            with open(source, 'r', encoding='utf-8') as f:
                data = json.load(f)
        elif isinstance(source, dict):
            data = source
        else:
            raise ValueError(f"不支持的 source 类型: {type(source)}")
        
        raw_messages = data.get('messages', [])
        messages = []
        
        for raw_msg in raw_messages:
            try:
                content = raw_msg.get('content', {})
                text = self._extract_text_from_content(content)
                if not text:
                    continue
                
                msg = Message.from_qq_export(raw_msg)
                msg.text = text
                messages.append(msg)
            except Exception as e:
                print(f"警告：跳过无效消息 {raw_msg.get('id')}: {e}")
                continue
        
        return messages
    
    def _extract_text_from_content(self, content: dict) -> str:
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
