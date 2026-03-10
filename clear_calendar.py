"""一次性脚本 - 删除日历中的所有事件（用完即删）"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from dotenv import load_dotenv
load_dotenv()

from ddlmanager.config import Config
from ddlmanager.services import CalendarService

cal = CalendarService(url=Config.CALDAV_URL, username=Config.CALDAV_USER, password=Config.CALDAV_PASS)
if not cal.connect():
    print("连接失败")
    sys.exit(1)

events = cal.list_events()
print(f"共 {len(events)} 个事件")

if not events:
    sys.exit(0)

answer = input("确认删除所有事件？(yes/no): ").strip()
if answer != "yes":
    print("已取消")
    sys.exit(0)

ok = 0
for ev in events:
    if cal.delete_event(ev['uid']):
        print(f"  已删除: {ev['summary']}")
        ok += 1
    else:
        print(f"  失败: {ev['summary']}")

print(f"\n完成，删除 {ok}/{len(events)} 个事件")
