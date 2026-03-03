"""日历服务 - 封装 CalDAV 操作"""
import uuid
from datetime import datetime
import icalendar
import caldav
from typing import List, Dict
from ..models import Event


class CalendarService:
    """CalDAV 日历服务
    
    为什么要封装？
    - 隔离第三方库（caldav、icalendar）的具体实现
    - 统一异常处理和日志记录
    - 方便后续支持其他日历服务（Google Calendar、Outlook 等）
    """
    
    def __init__(self, url: str, username: str, password: str):
        """
        初始化 CalDAV 客户端
        注意，qq的dav.qq.com不要增加https://
        """
        
        self.client = caldav.DAVClient(url, username=username, password=password)
        self.calendar = None
    
    def connect(self) -> bool:
        """连接到日历并获取主日历"""
        try:
            principal = self.client.principal()
            calendars = principal.calendars()
            if calendars:
                self.calendar = calendars[0]
                print(f"已连接到日历: {self.calendar.name}")
                return True
            else:
                print("错误：未找到可用日历")
                return False
        except Exception as e:
            print(f"连接日历失败: {e}")
            return False
    
    def list_events(self) -> List[Dict]:
        """列出日历中的所有事件"""
        if not self.calendar:
            raise RuntimeError("请先调用 connect() 连接日历")
        
        events_list = []
        events = self.calendar.events()
        
        for event in events:
            ical_component = event.icalendar_instance
            for component in ical_component.walk():
                if component.name == "VEVENT":
                    events_list.append({
                        'summary': str(component.get('summary', '')),
                        'start': component.get('dtstart').dt if component.get('dtstart') else None,
                        'uid': str(component.get('uid', ''))
                    })
        
        return events_list
    
    def save_event(self, event: Event) -> bool:
        """保存事件到日历
        
        Args:
            event: Event 对象
            
        Returns:
            bool: 是否成功保存
        """
        if not self.calendar:
            raise RuntimeError("请先调用 connect() 连接日历")
        
        try:
            ical_event = icalendar.Event()
            
            uid = event.uid or str(uuid.uuid1()).upper()
            ical_event.add('uid', uid)
            ical_event.add('dtstamp', datetime.now())
            ical_event.add('summary', event.summary)
            ical_event.add('description', event.description)
            ical_event.add('dtstart', event.start_datetime)
            ical_event.add('dtend', event.end_datetime)
            
            event_data = ical_event.to_ical()
            self.calendar.save_event(event_data)
            
            print(f"✓ 已保存事件: {event.summary}")
            return True
        except Exception as e:
            print(f"✗ 保存事件失败 {event.summary}: {e}")
            return False
    
    def save_events_batch(self, events: List[Event]) -> int:
        """批量保存事件
        
        Returns:
            int: 成功保存的事件数量
        """
        success_count = 0
        for event in events:
            if self.save_event(event):
                success_count += 1
        return success_count
