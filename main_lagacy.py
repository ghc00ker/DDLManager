# Please install OpenAI SDK first: `pip3 install openai`
import os
import sys
import json
import uuid
from datetime import datetime
import icalendar
import caldav
from openai import OpenAI

from dotenv import load_dotenv


def extract_text_from_content(content: dict) -> str:
    # 优先使用 content.text，如果不可用则从 content.elements 按序拼接 text 片段
    if not content:
        return ''
    text = content.get('text')
    if text and str(text).strip():
        return str(text).strip()

    parts = []
    elements = content.get('elements') or []
    for el in elements:
        t = el.get('type')
        data = el.get('data') or {}
        if t == 'text':
            parts.append(str(data.get('text') or ''))
        elif t == 'at':
            # 保留 @ 用户名，便于检索
            parts.append('@' + str(data.get('name') or data.get('uid') or ''))
        elif t == 'face':
            # 可选地保留表情占位
            parts.append('[' + str(data.get('name') or '表情') + ']')
        elif t == 'file':
            parts.append('[文件: ' + str(data.get('filename') or '') + ']')
        elif t == 'image':
            parts.append('[图片]')
    return ''.join(parts).strip()


def format_messages_for_prompt(messages: list, max_items: int = 5000) -> str:
    out_lines = []
    for m in (messages or [])[:max_items]:
        mid = m.get('id')
        ts = m.get('time') or m.get('timestamp')
        sender = m.get('sender') or {}
        sender_name = sender.get('name') or sender.get('uid') or ''
        content = m.get('content') or {}
        text = extract_text_from_content(content)
        if not text:
            continue
        out_lines.append(f"[{ts}] {sender_name}: {text}")
    return '\n'.join(out_lines)


def main():
    # 在函数内加载 .env（指定路径，确保调试时也能找到）
    from pathlib import Path
    env_path = Path(__file__).parent / '.env'
    load_dotenv(env_path)
    
    # 从环境变量读取 CalDAV 配置
    url = os.getenv('CALDAV_URL')
    username = os.getenv('CALDAV_USER')
    password = os.getenv('CALDAV_PASS')
    
    if not url or not username or not password:
        print('错误：请在 .env 文件中设置 CALDAV_URL, CALDAV_USER 和 CALDAV_PASS')
        sys.exit(1)
    
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
    print('--------------------------------------------------')
    # 从环境变量读取 API Key（而不是硬编码）
    API_KEY = os.getenv('DEEPSEEK_API_KEY')
    BASE_URL = os.getenv('DEEPSEEK_BASE_URL') or 'https://api.deepseek.com'
    
    if not API_KEY:
        print('错误：请在 .env 文件中设置 DEEPSEEK_API_KEY')
        sys.exit(1)

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    # 导入json文件
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'data\group_792340423_20260223_230254.json'
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print('无法读取输入文件:', e)
        sys.exit(1)

    messages = data.get('messages', [])
    if not messages:
        print('没有找到 messages 字段或为空')
        sys.exit(0)

    # 构造简短可读提示，默认只取最近 50 条以控制 token
    max_items = int(os.environ.get('MAX_MESSAGES', '5000'))
    prompt_messages_text = format_messages_for_prompt(messages, max_items=max_items)

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
            },
            {
                "start_datetime": {
                    "year": 2025,
                    "month": 4,
                    "day": 15,
                    "hour": 14,
                    "minute": 30
                },
                "end_datetime": {
                    "year": 2025,
                    "month": 4,
                    "day": 15,
                    "hour": 16,
                    "minute": 45
                },
                "summary": "事件二",
                "description": "细节补充"
            },
        ]
    }
    '''
    user_prompt = '下面是聊天记录，最多前 {} 条）：\n\n{}'.format(max_items, prompt_messages_text)

    try:
        resp = client.chat.completions.create(
            model='deepseek-chat',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            response_format={
                'type': 'json_object'
            },
            stream=False,
        )
        print(resp.choices[0].message.content)
        json_data = json.loads(resp.choices[0].message.content)
        print(json_data)
        new_events = []
        # for item in json_data["ddl"]:
        #     event = icalendar.Event()
        #     start_datetime = item.get('start_datetime')
        #     end_datetime = item.get('end_datetime')
        #     summary = item.get('summary')
        #     description = item.get('description')
            
        #     uid = str(uuid.uuid1()).upper()
        #     event.add('uid', uid)
        #     event.add('dtstamp', datetime.now()) 
        #     event.add('summary', summary)
        #     event.add('description', description)
        #     event.add('dtstart', datetime(
        #         start_datetime.get('year'),
        #         start_datetime.get('month'),
        #         start_datetime.get('day'),
        #         start_datetime.get('hour'),
        #         start_datetime.get('minute'),
        #     ))
        #     event.add('dtend', datetime(
        #         end_datetime.get('year'),
        #         end_datetime.get('month'),
        #         end_datetime.get('day'),
        #         end_datetime.get('hour'),
        #         end_datetime.get('minute'),
        #     ))
            
        #     new_event_data = event.to_ical()  # 注意：这里直接用event.to_ical()
        #     calendar.save_event(new_event_data)
    except Exception as e:
        print('调用 AI 接口出错:', e)


if __name__ == '__main__':
    main()
