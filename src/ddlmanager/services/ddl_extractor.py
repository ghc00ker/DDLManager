"""DDL 提取器 - 核心业务逻辑"""
from datetime import datetime
from typing import List
from ..models import Message, Event
from .ai_client import AIClient
from ..config import Config
from .storage import StorageService
class DDLExtractor:
    """DDL 提取器 - 协调消息解析、AI 分析、事件生成
    
    这是整个流程的编排器（Orchestrator）：
    1. 接收消息列表
    2. 调用 AI 提取 DDL
    3. 转换为标准 Event 对象
    """
    
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client
    
    def extract(self, messages: List[Message], watermark: datetime) -> List[Event]:
        """从消息中提取 DDL 事件
        
        Args:
            messages: 已解析的消息列表
            groupname: 群聊名称
            
        Returns:
            List[Event]: 提取出的事件对象列表
        """
        if not messages:
            print("警告：消息列表为空")
            return []
        
        print(f"开始分析 {len(messages)} 条消息...")
        
        ddl_items = self.ai_client.extract_deadlines(messages, watermark)
        
        events = []
        for item in ddl_items:
            try:
                event = Event.from_ai_response(item)
                events.append(event)
            except Exception as e:
                print(f"警告：跳过无效事件 {item.get('summary', '未知')}: {e}")
                continue
        
        print(f"成功提取 {len(events)} 个事件")
        return events
