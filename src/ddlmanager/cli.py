"""命令行入口 - 主流程编排"""
from datetime import datetime
import json
import sys
from pathlib import Path
from .config import Config
from .parsers import QQParser
from .services import AIClient, CalendarService, DDLExtractor
from .models import Event
from .services.storage import StorageService
from typing import List
import threading
import time
import itertools

def info(msg: str):
    """系统提示"""
    return (f"> {msg}")

class Spinner:
    """CLI 等待动画（上下文管理器）"""
    """LLM Generate"""
    def __init__(self, message: str = "处理中"):
        self.message = message
        self._stop = threading.Event()
        self._thread = None

    def _spin(self):
        chars = itertools.cycle('⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏')
        start = time.time()
        while not self._stop.is_set():
            elapsed = time.time() - start
            print(f"\r{next(chars)} {self.message}... ({elapsed:.0f}s)", end="", flush=True)
            self._stop.wait(0.1)
        elapsed = time.time() - start
        print(f"\r✓ {self.message} 完成 ({elapsed:.1f}s)   ")

    def __enter__(self):
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *args):
        self._stop.set()
        self._thread.join()

def confirm(prompt: str = "是否继续？(y/n): ") -> bool:
    """通用确认，只接受 y/n"""
    while True:
        choice = input(prompt).strip().lower()
        if choice in ('y', 'n'):
            return choice == 'y'
        print("> 请输入 y 或 n")

def review_events(events: List[Event]) -> List[Event]:
    """逐个审查事件，返回通过审查的事件列表"""
    if not events:
        return []

    approved = []
    print(f"\n{'='*50}")
    print(f"共 {len(events)} 个事件待审查")
    print(f"{'='*50}")

    for i, event in enumerate(events, 1):
        print(f"\n[{i}/{len(events)}]")
        print(f"  标题: {event.summary}")
        print(f"  开始: {event.start_datetime:%Y-%m-%d %H:%M}")
        print(f"  结束: {event.end_datetime:%Y-%m-%d %H:%M}")
        print(f"  描述: {event.description}")

        if confirm("  是否保留该事件？(y/n): "):
            approved.append(event)
            print("  → 已保留")
        else:
            print("  → 已跳过")

    print(f"\n审查完毕：{len(approved)}/{len(events)} 个事件通过")
    return approved

def main():
    """主流程：读取聊天记录 -> AI 分析 -> 保存到日历
    
    流程设计原则：
    1. 快速失败（配置验证）
    2. 职责分离（每个步骤调用对应的服务）
    3. 清晰的错误提示
    """
    
    # 1. 配置验证
    if not Config.DEEPSEEK_API_KEY:
        Config.DEEPSEEK_API_KEY = Config.load_api_key_from_file('apikey.txt')
    
    if not Config.validate():
        sys.exit(1)
    
    # 2. 读取输入文件
    input_path = sys.argv[1] if len(sys.argv) > 1 else Config.DATA_PATH
    
    if not Path(input_path).exists():
        print(f'错误：文件不存在 {input_path}')
        sys.exit(1)
    
    # 获取群聊名称
    groupname: str
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        groupname = (data.get("chatInfo")).get("name")
    
    # 3. 解析消息
    parser = QQParser()
    try:
        messages = parser.parse(input_path)
        print(f"已解析 {len(messages)} 条消息")
    except Exception as e:
        print(f'解析消息失败: {e}')
        sys.exit(1)
    
    if not messages:
        print('没有找到有效消息')
        sys.exit(0)
        
    for message in messages:
        print(message.format_message_for_prompt() + "\n")
    
    # 第一处人工审查 
    if not confirm(f"\n以上为 {len(messages)} 条消息，是否发送给 AI 分析？(y/n): "):
        print("已取消")
        sys.exit(0)
        
    # 4. AI 提取 DDL
    ai_client = AIClient(
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    extractor = DDLExtractor(ai_client)
    
    
    # 加载storage
    try:
        storage = StorageService()
        watermark = datetime.fromtimestamp(storage.get_watermark(groupname))
    except Exception as e:
        print("加载storage失败")
        sys.exit(1)
    # 开始分析
    try:
        with Spinner("LLM分析中"):
            events = extractor.extract(messages, watermark)
    except Exception as e:
        print(f'AI 分析失败: {e}')
        sys.exit(1)
    if not events:
        print('未提取到任何事件')
        sys.exit(0)
        
    for event in events:
        print(event.print_Event() + "/n")
        
    # 第二个人工审查
    events = review_events(events)
    
    print("以下为通过人工审查的Event")
    
    for event in events:
        print(event.print_Event())
        
    # 第三个人工审查
    if not confirm(f"\n以上为 {len(events)} 个Event，是否与日历同步？(y/n): "):
        print("已取消")
        sys.exit(0)
        
    # 5. 保存到日历
    calendar = CalendarService(
        url=Config.CALDAV_URL,
        username=Config.CALDAV_USER,
        password=Config.CALDAV_PASS
    )
    
    if not calendar.connect():
        print('连接日历失败')
        sys.exit(1)
    
    print(f"\n开始保存 {len(events)} 个事件到日历...")
    success_count = calendar.save_events_batch(events)
    
    print(f"\n完成！成功保存 {success_count}/{len(events)} 个事件")
    if messages:
        storage.update_watermark(groupname, messages[-1].timestamp)


if __name__ == '__main__':
    main()
