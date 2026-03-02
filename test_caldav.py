from datetime import datetime
import caldav
import icalendar
import uuid
from caldav.objects import Event
 
# 连接到 CalDAV 服务器
url = "dav.qq.com"
username = "2663469147@qq.com"
password = "vxwkkfcsoiyodjca"
client = caldav.DAVClient(url, username=username, password=password)
 
# 获取主日历
principal = client.principal()
calendars = principal.calendars()
if calendars:
    calendar = calendars[0]
    print(f"Using calendar: {calendar.name}")
    # 获取所有事件
    events = calendar.events()
    print(1)
for event in events:
    # 使用 icalendar_instance 访问
    ical_component = event.icalendar_instance
    # 遍历所有组件，找到 VEVENT 组件
    for component in ical_component.walk():
        if component.name == "VEVENT":
            # 主题 (summary) 可以通过 get 方法获取
            event_summary = component.get('summary')
            if event_summary:
                print(f"事件主题: {event_summary}")

            # 同样可以获取其他属性
            dtstart = component.get('dtstart')
            if dtstart:
                print(f"开始时间: {dtstart.dt}")
                
            uid = component.get('uid')
            if uid:
                print(f"uid: {uid}")
# 新建新的event
new_event = icalendar.Event()
uid = str(uuid.uuid1()).upper()
new_event.add('uid', uid)
new_event.add('dtstamp', datetime.now()) 
# 时间戳，event的创建时间
new_event.add('dtstart', datetime(2026, 4, 1, 10, 0))
new_event.add('dtend', datetime(2026, 4, 1, 11, 0))
new_event.add('description', '这是一个测试')
new_event.add('summary', '测试事件')

new_event_data = new_event.to_ical()  # 注意：这里直接用event.to_ical()
calendar.save_event(new_event_data)
