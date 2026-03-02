"""消息数据模型"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Message:
    """聊天消息的统一数据结构"""
    id: str
    sender_name: str
    sender_uid: Optional[str]
    text: str
    timestamp: datetime
    
    @classmethod
    def from_qq_export(cls, raw_message: dict) -> 'Message':
        """从 QQ 导出的 JSON 格式创建消息对象"""
        mid = raw_message.get('id', '')
        ts = raw_message.get('time') or raw_message.get('timestamp')
        sender = raw_message.get('sender') or {}
        sender_name = sender.get('name') or sender.get('uid') or ''
        sender_uid = sender.get('uid')
        content = raw_message.get('content') or {}
        
        text = str(content.get('text', ''))
        
        try:
            dt = datetime.fromtimestamp(int(ts)) if ts else datetime.now()
        except:
            dt = datetime.now()
        
        return cls(
            id=str(mid),
            sender_name=sender_name,
            sender_uid=sender_uid,
            text=text,
            timestamp=dt
        )
