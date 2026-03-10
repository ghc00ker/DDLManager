"""CalDAV 日历管理 - 交互式增删改查"""
from datetime import datetime
from typing import List, Dict, Optional

from ..config import Config
from ..models import Event
from ..services import CalendarService
from .helpers import confirm


def _print_event_list(events: List[Dict]):
    """打印事件列表（带序号）"""
    if not events:
        print("  （暂无事件）")
        return
    for i, ev in enumerate(events, 1):
        start = ev['start'].strftime('%Y-%m-%d %H:%M') if ev.get('start') else '未知'
        end = ev['end'].strftime('%Y-%m-%d %H:%M') if ev.get('end') else '未知'
        print(f"  {i}. [{start} ~ {end}] {ev['summary']}")


def _select_event(events: List[Dict], prompt: str = "请输入事件编号: ") -> Optional[Dict]:
    """让用户从事件列表中选择一个"""
    if not events:
        print("没有可选的事件")
        return None
    _print_event_list(events)
    while True:
        raw = input(prompt).strip()
        try:
            idx = int(raw)
            if 1 <= idx <= len(events):
                return events[idx - 1]
        except ValueError:
            pass
        print(f"> 请输入 1-{len(events)} 之间的数字")


def _input_datetime(prompt: str) -> Optional[datetime]:
    """交互式输入日期时间，留空返回 None"""
    while True:
        raw = input(f"{prompt}（格式 YYYY-MM-DD HH:MM，留空跳过）: ").strip()
        if not raw:
            return None
        try:
            return datetime.strptime(raw, '%Y-%m-%d %H:%M')
        except ValueError:
            print("> 格式错误，请使用 YYYY-MM-DD HH:MM")


def _handle_list(calendar: CalendarService):
    """查看所有事件"""
    events = calendar.list_events()
    print(f"\n日历中共有 {len(events)} 个事件：")
    if not events:
        return
    for i, ev in enumerate(events, 1):
        start = ev['start'].strftime('%Y-%m-%d %H:%M') if ev.get('start') else '未知'
        end = ev['end'].strftime('%Y-%m-%d %H:%M') if ev.get('end') else '未知'
        desc = ev.get('description', '')
        desc_preview = (desc[:30] + '...') if len(desc) > 30 else desc
        print(f"  {i}. [{start} ~ {end}] {ev['summary']}")
        if desc_preview:
            print(f"     描述: {desc_preview}")


def _handle_add(calendar: CalendarService):
    """手动新增事件"""
    print("\n--- 新增事件 ---")
    summary = input("标题: ").strip()
    if not summary:
        print("标题不能为空，已取消")
        return

    start_dt = _input_datetime("开始时间")
    if not start_dt:
        print("开始时间不能为空，已取消")
        return

    end_dt = _input_datetime("结束时间")
    if not end_dt:
        end_dt = start_dt

    description = input("描述（可留空）: ").strip()

    event = Event(
        summary=summary,
        description=description,
        start_datetime=start_dt,
        end_datetime=end_dt,
    )

    print(f"\n即将创建事件:")
    print(event.print_Event())
    if confirm("确认创建？(y/n): "):
        if calendar.save_event(event):
            print("事件创建成功")
        else:
            print("事件创建失败")
    else:
        print("已取消")


def _handle_edit(calendar: CalendarService):
    """修改事件：选择后逐字段编辑，留空保持原值"""
    events = calendar.list_events()
    if not events:
        print("\n日历中没有事件")
        return

    print("\n--- 修改事件 ---")
    selected = _select_event(events)
    if not selected:
        return

    uid = selected['uid']
    print(f"\n当前值：")
    print(f"  标题: {selected['summary']}")
    start_str = selected['start'].strftime('%Y-%m-%d %H:%M') if selected.get('start') else '未知'
    end_str = selected['end'].strftime('%Y-%m-%d %H:%M') if selected.get('end') else '未知'
    print(f"  开始: {start_str}")
    print(f"  结束: {end_str}")
    print(f"  描述: {selected.get('description', '')}")
    print("（留空表示保持原值）")

    new_summary = input(f"新标题 [{selected['summary']}]: ").strip() or selected['summary']
    new_start = _input_datetime("新开始时间") or selected.get('start')
    new_end = _input_datetime("新结束时间") or selected.get('end')
    new_desc = input(f"新描述 [{selected.get('description', '')}]: ").strip()
    if not new_desc:
        new_desc = selected.get('description', '')

    updated = Event(
        summary=new_summary,
        description=new_desc,
        start_datetime=new_start,
        end_datetime=new_end,
    )

    print(f"\n修改后：")
    print(updated.print_Event())
    if confirm("确认修改？(y/n): "):
        if calendar.update_event(uid, updated):
            print("事件修改成功")
        else:
            print("事件修改失败")
    else:
        print("已取消")


def _handle_delete(calendar: CalendarService):
    """删除事件"""
    events = calendar.list_events()
    if not events:
        print("\n日历中没有事件")
        return

    print("\n--- 删除事件 ---")
    selected = _select_event(events)
    if not selected:
        return

    start_str = selected['start'].strftime('%Y-%m-%d %H:%M') if selected.get('start') else '未知'
    print(f"\n即将删除: [{start_str}] {selected['summary']}")
    if confirm("确认删除？(y/n): "):
        if calendar.delete_event(selected['uid']):
            print("✓ 事件已删除")
        else:
            print("✗ 删除失败")
    else:
        print("已取消")


def _handle_batch_delete(calendar: CalendarService):
    """批量删除事件：支持多选编号、全选"""
    events = calendar.list_events()
    if not events:
        print("\n日历中没有事件")
        return

    print("\n--- 批量删除事件 ---")
    _print_event_list(events)
    print(f"  0. 全选")

    while True:
        raw = input("\n请输入要删除的编号（多个用逗号分隔，如 1,3,5）: ").strip()
        if raw == '0':
            selected = events
            break
        try:
            indices = [int(x.strip()) for x in raw.split(",")]
            selected = [events[i - 1] for i in indices if 1 <= i <= len(events)]
            if selected:
                break
        except (ValueError, IndexError):
            pass
        print(f"> 输入无效，请输入 0-{len(events)} 之间的数字")

    print(f"\n即将删除以下 {len(selected)} 个事件：")
    for ev in selected:
        start = ev['start'].strftime('%Y-%m-%d %H:%M') if ev.get('start') else '未知'
        print(f"  - [{start}] {ev['summary']}")

    if not confirm(f"确认删除这 {len(selected)} 个事件？(y/n): "):
        print("已取消")
        return

    ok, fail = 0, 0
    for ev in selected:
        if calendar.delete_event(ev['uid']):
            ok += 1
        else:
            print(f"  ✗ 删除失败: {ev['summary']}")
            fail += 1

    print(f"\n批量删除完成：成功 {ok} 个，失败 {fail} 个")


def run_calendar():
    """日历管理主入口 - 连接后进入子菜单循环"""
    if not Config.CALDAV_URL or not Config.CALDAV_USER or not Config.CALDAV_PASS:
        print("错误：缺少 CalDAV 配置，请在 .env 中设置 CALDAV_URL, CALDAV_USER, CALDAV_PASS")
        return

    calendar = CalendarService(
        url=Config.CALDAV_URL,
        username=Config.CALDAV_USER,
        password=Config.CALDAV_PASS,
    )

    if not calendar.connect():
        print("连接日历失败")
        return

    MENU = """
--- 日历管理 ---
  1. 查看所有事件
  2. 新增事件
  3. 修改事件
  4. 删除事件
  5. 批量删除事件
  0. 返回主菜单
"""

    handlers = {
        '1': _handle_list,
        '2': _handle_add,
        '3': _handle_edit,
        '4': _handle_delete,
        '5': _handle_batch_delete,
    }

    while True:
        print(MENU)
        choice = input("请选择: ").strip()

        if choice == '0':
            return

        handler = handlers.get(choice)
        if handler:
            try:
                handler(calendar)
            except Exception as e:
                print(f"操作失败: {e}")
        else:
            print("> 无效选项，请重新选择")
