"""消息数据模型"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from typing import List
from collections import deque
from ..config import Config
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
        try:
            ts = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            return f"[{ts}] {self.sender_name}: {self.text}"
        except Exception as e:
            print(f"格式化消息时出错: {e}")
            return ""

    @classmethod
    def get_messages_with_content(cls, messages: List['Message'], watermark: datetime) -> List['Message']:
        """取 watermark 之前最近 CONTENT_NUM 条作为上下文，加上 watermark 之后的所有新消息"""
        context_deq = deque(maxlen=Config.CONTENT_NUM)
        new_start = len(messages)

        for i, message in enumerate(messages):
            if message.timestamp <= watermark:
                context_deq.append(message)
            else:
                new_start = i
                break

        context = list(context_deq)
        print(f"共获取了{len(context)}条上下文消息")

        if new_start >= len(messages):
            return context

        return context + messages[new_start:]
        