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
    
    def format_message_for_prompt(self) -> str:
        """格式化一条消息为 AI 可读的文本"""
        line: str = ""
        try:
            ts = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            line = (f"[{ts}] {self.sender_name}: {self.text}")
        except:
            print("格式化消息为 AI 可读的文本时出错")
            
        return line