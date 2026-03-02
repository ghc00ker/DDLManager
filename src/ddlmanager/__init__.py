"""DDLManager - 智能 DDL 管理工具

这是顶层的 __init__.py，导出最常用的接口，让外部使用更方便。

使用方式：
    # 方式 1: 使用子包（推荐，职责清晰）
    from ddlmanager.parsers import QQParser
    from ddlmanager.services import AIClient, CalendarService
    from ddlmanager.models import Message, Event
    
    # 方式 2: 从顶层导入（快捷方式）
    from ddlmanager import QQParser, AIClient, Event
"""

# 导出核心类（最常用的接口）
from .models import Message, Event
from .parsers import QQParser, MessageParser
from .services import AIClient, CalendarService, DDLExtractor
from .config import Config

__version__ = '0.1.0'

__all__ = [
    # 数据模型
    'Message',
    'Event',
    # 解析器
    'QQParser',
    'MessageParser',
    # 服务
    'AIClient',
    'CalendarService',
    'DDLExtractor',
    # 配置
    'Config',
]
