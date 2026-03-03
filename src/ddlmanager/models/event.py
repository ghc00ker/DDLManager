"""事件/DDL 数据模型"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Event:
    """日历事件的统一数据结构"""
    summary: str
    description: str
    start_datetime: datetime
    end_datetime: datetime
    uid: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典格式（用于 API 响应或序列化）"""
        return {
            'summary': self.summary,
            'description': self.description,
            'start_datetime': self.start_datetime.isoformat(),
            'end_datetime': self.end_datetime.isoformat(),
            'uid': self.uid
        }
    
    def print_Event(self) -> 'str':
        line:str = ""
        line += "Event: "
        line += self.summary
        line += " start: "
        line += self.start_datetime.strftime("%Y-%m-%d %H:%M:%S")
        line += " end: "
        line += self.end_datetime.strftime("%Y-%m-%d %H:%M:%S")
        line += " description: "
        line += self.description
        return line
    
    @classmethod
    def from_ai_response(cls, item: dict) -> 'Event':
        """从 AI 返回的 JSON 格式创建事件对象"""
        start = item.get('start_datetime', {})
        end = item.get('end_datetime', {})
        
        start_dt = datetime(
            start.get('year', 2026),
            start.get('month', 1),
            start.get('day', 1),
            start.get('hour', 0),
            start.get('minute', 0)
        )
        
        end_dt = datetime(
            end.get('year', 2026),
            end.get('month', 1),
            end.get('day', 1),
            end.get('hour', 0),
            end.get('minute', 0)
        )
        
        return cls(
            summary=item.get('summary', '未命名事件'),
            description=item.get('description', ''),
            start_datetime=start_dt,
            end_datetime=end_dt
        )
