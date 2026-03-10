"""通用 CLI 工具 - Spinner、确认、事件审查等共享组件"""
import threading
import time
import itertools
from typing import List
from ..models import Event


def info(msg: str) -> str:
    """系统提示"""
    return f"> {msg}"


class Spinner:
    """CLI 等待动画（上下文管理器）"""

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
