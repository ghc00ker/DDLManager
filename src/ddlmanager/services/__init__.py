"""服务层包 - 业务逻辑和外部服务封装

这个 __init__.py 导出：
- AIClient: AI API 调用
- CalendarService: 日历操作
- DDLExtractor: DDL 提取核心逻辑

使用方式：
    from ddlmanager.services import AIClient, CalendarService, DDLExtractor
"""

from .ai_client import AIClient
from .calendar_service import CalendarService
from .ddl_extractor import DDLExtractor

__all__ = ['AIClient', 'CalendarService', 'DDLExtractor']
