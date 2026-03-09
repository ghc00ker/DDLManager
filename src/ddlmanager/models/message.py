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
        line: str = ""
        try:
            ts = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            line = (f"[{ts}] {self.sender_name}: {self.text}")
        except:
            print("格式化消息为 AI 可读的文本时出错")
            
        return line
    
    @classmethod
    def get_messages_with_content(cls, messages: List['Message'], watermark: datetime) -> List['Message']:
        ret_deq = deque(maxlen = Config.CONTENT_NUM)
        ret: List[Message]
        newest_index: int
        for i, message in enumerate(messages):
            if message.timestamp <= watermark:
                ret_deq.append(message)
            else:
                ret = list(ret_deq)
                print(f"共获取了{len(ret)}条content message")
                newest_index = i
                break
        for message in messages[newest_index:]:
            ret.append(message)
        return ret
        