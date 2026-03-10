"""主菜单 - 交互式菜单循环，路由到各功能模块"""
from .extract import run_extract
from .calendar_mgmt import run_calendar


BANNER = """
╔══════════════════════════════════╗
║         DDL Manager              ║
╚══════════════════════════════════╝
"""

MAIN_MENU = """
--- 主菜单 ---
  1. 提取 DDL（从聊天记录）
  2. 管理日历（CalDAV）
  0. 退出
"""


def main():
    """主菜单循环"""
    print(BANNER)

    while True:
        print(MAIN_MENU)
        choice = input("请选择: ").strip()

        if choice == '1':
            try:
                run_extract()
            except KeyboardInterrupt:
                print("\n已中断，返回主菜单")
        elif choice == '2':
            try:
                run_calendar()
            except KeyboardInterrupt:
                print("\n已中断，返回主菜单")
        elif choice == '0':
            print("再见！")
            break
        else:
            print("> 无效选项，请重新选择")
