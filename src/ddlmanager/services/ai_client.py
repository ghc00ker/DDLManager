"""AI 客户端 - 封装 DeepSeek/OpenAI API 调用"""
import json
from typing import List, Dict
from openai import OpenAI
from ..models import Message


class AIClient:
    """DeepSeek AI 客户端
    
    为什么要封装？
    - 统一错误处理和重试逻辑
    - 方便切换不同的 AI 提供商（只需改这个类）
    - 可以加入日志、计费统计等功能
    """
    
    def __init__(self, api_key: str, base_url: str = 'https://api.deepseek.com'):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = 'deepseek-chat'
    
    def extract_deadlines(self, messages: List[Message], max_messages: int = 5000) -> List[Dict]:
        """从消息列表中提取 DDL 和事件
        
        Args:
            messages: 消息对象列表
            max_messages: 最多处理的消息数量（控制 token）
            
        Returns:
            List[Dict]: AI 返回的 DDL 列表（原始格式）
        """
        prompt_text = self._format_messages_for_prompt(messages[:max_messages])
        
        system_prompt = '''
我是一个学生，而你是我的私人秘书，我需要你详细地把所有DeadLines和事件列出来，标明时间和内容
以JSON格式返回，字段包括：起始时间的年，月，日，小时，分钟，结束时间的年，月，日，小时，分钟，标题，详细内容
例子：
{
    "ddl": [
        {
            "start_datetime": {
                "year": 2024,
                "month": 3,
                "day": 15,
                "hour": 14,
                "minute": 30
            },
            "end_datetime": {
                "year": 2024,
                "month": 3,
                "day": 15,
                "hour": 16,
                "minute": 45
            },
            "summary": "事件一",
            "description": "细节补充"
        }
    ]
}
'''
        
        user_prompt = f'下面是聊天记录（最多前 {max_messages} 条）：\n\n{prompt_text}'
        
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            response_format={'type': 'json_object'},
            stream=False,
        )
        
        json_data = json.loads(resp.choices[0].message.content)
        return json_data.get('ddl', [])
    
    def _format_messages_for_prompt(self, messages: List[Message]) -> str:
        """格式化消息为 AI 可读的文本"""
        lines = []
        for msg in messages:
            ts = msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            lines.append(f"[{ts}] {msg.sender_name}: {msg.text}")
        return '\n'.join(lines)
