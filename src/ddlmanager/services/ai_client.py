"""AI 客户端 - 封装 DeepSeek/OpenAI API 调用"""
from datetime import datetime
import json
from typing import List, Dict
from openai import OpenAI
from ..models import Message
from ..config import Config
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
    
    def extract_deadlines(self, messages: List[Message], watermark: datetime) -> List[Dict]:
        """从消息列表中提取 DDL 和事件
        
        Args:
            messages: 消息对象列表
            max_messages: 最多处理的消息数量（控制 token）
            
        Returns:
            List[Dict]: AI 返回的 DDL 列表（原始格式）
        """
        prompt_message = Message.get_messages_with_content(messages, watermark)
        # 格式化聊天记录
        count = 0
        prompt_text: str = "以下为上下文背景："
        for message in prompt_message:
            if (message.timestamp < watermark):
                prompt_text += message.format_message_for_prompt()
                prompt_text += "\n"
                count += 1
            else:
                break
        prompt_text += "\n 以下为待分析的内容：\n"
        for message in prompt_message[count:]:
            prompt_text += message.format_message_for_prompt()
            prompt_text += "\n"
            count += 1
        # print("--------------------------------------------------")
        # print("prompt_text:")
        # print(prompt_text)
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
        
        user_prompt = f'下面是聊天记录：\n\n{prompt_text}'

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            response_format={'type': 'json_object'},
            stream=False,
        )
        # print("--------------------------------------------------")
        # print("response: ")
        json_data = json.loads(resp.choices[0].message.content)
        # for event in resp.choices[0]:
        #     print(event)
        return json_data.get('ddl', [])
