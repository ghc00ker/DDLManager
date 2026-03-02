"""消息解析器包

这个 __init__.py 导出：
- MessageParser: 抽象基类
- QQParser: QQ 消息解析实现

使用方式：
    from ddlmanager.parsers import QQParser
    parser = QQParser()
    messages = parser.parse('path/to/qq_export.json')
"""

from .base import MessageParser
from .qq_parser import QQParser

__all__ = ['MessageParser', 'QQParser']
