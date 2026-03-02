"""数据模型包 - 统一的数据结构定义

这个 __init__.py 的作用：
1. 把子模块的类导入到包级别
2. 让外部可以直接 `from ddlmanager.models import Message, Event`
   而不需要写 `from ddlmanager.models.message import Message`
"""

from .message import Message
from .event import Event

__all__ = ['Message', 'Event']
