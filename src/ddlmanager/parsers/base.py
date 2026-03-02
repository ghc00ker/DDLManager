"""消息解析器的抽象基类"""
from abc import ABC, abstractmethod
from typing import List
from ..models import Message


class MessageParser(ABC):
    """消息解析器的接口定义
    
    为什么需要抽象类？
    - 定义统一接口，让所有消息源（QQ、微信、文本）都实现相同的 parse 方法
    - 后续可以轻松切换或扩展新的消息源
    """
    
    @abstractmethod
    def parse(self, source) -> List[Message]:
        """解析消息源，返回消息列表
        
        Args:
            source: 可以是文件路径、字典、或任何消息源
            
        Returns:
            List[Message]: 标准化的消息对象列表
        """
        pass
