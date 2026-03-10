"""DDL 提取流程 - 读取聊天记录 -> AI 分析 -> 审查 -> 同步日历"""
import json
from pathlib import Path
from typing import List, Dict

from ..config import Config
from ..parsers import QQParser
from ..services import AIClient, CalendarService, DDLExtractor
from ..services.storage import StorageService
from .helpers import Spinner, confirm, review_events


def _scan_data_files(data_path: str) -> List[Dict]:
    """扫描 DATA_PATH 目录下所有 .json 文件，读取 chatInfo.name 作为显示名称

    Returns:
        [{"path": Path, "name": str}, ...]
    """
    p = Path(data_path)
    if not p.is_dir():
        print(f"错误：DATA_PATH 不是有效目录 {data_path}")
        return []

    results = []
    for f in sorted(p.glob("*.json")):
        try:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
            name = (data.get("chatInfo") or {}).get("name")
            if name:
                results.append({"path": f, "name": name})
            else:
                results.append({"path": f, "name": f"（未知群名）{f.name}"})
        except Exception:
            results.append({"path": f, "name": f"（读取失败）{f.name}"})

    return results


def _select_files(data_path: str) -> List[Dict]:
    """展示群聊名称列表，让用户选择要分析的文件"""
    entries = _scan_data_files(data_path)
    if not entries:
        print(f"错误：{data_path} 下没有找到 .json 文件")
        return []

    print(f"\n在 {data_path} 下找到 {len(entries)} 个聊天记录：")
    for i, entry in enumerate(entries, 1):
        print(f"  {i}. {entry['name']}")
    print(f"  0. 全选")

    while True:
        raw = input("\n请输入编号（多个用逗号分隔，如 1,3）: ").strip()
        if raw == "0":
            return entries

        try:
            indices = [int(x.strip()) for x in raw.split(",")]
            selected = [entries[i - 1] for i in indices if 1 <= i <= len(entries)]
            if selected:
                return selected
        except (ValueError, IndexError):
            pass
        print("> 输入无效，请重新选择")


def _process_single_file(entry: Dict):
    """对单个聊天记录执行完整的提取 -> 审查 -> 同步流程

    Args:
        entry: {"path": Path, "name": str}
    """
    file_path = entry["path"]
    groupname = entry["name"]

    print(f"\n{'='*50}")
    print(f"处理: {groupname}（{file_path.name}）")
    print(f"{'='*50}")

    parser = QQParser()
    try:
        messages = parser.parse(str(file_path))
        print(f"已解析 {len(messages)} 条消息")
    except Exception as e:
        print(f"解析消息失败: {e}")
        return

    if not messages:
        print("没有找到有效消息")
        return

    for message in messages:
        print(message.format_message_for_prompt())

    if not confirm(f"\n以上为 {len(messages)} 条消息，是否发送给 AI 分析？(y/n): "):
        print("已跳过该文件")
        return

    ai_client = AIClient(
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    extractor = DDLExtractor(ai_client)

    try:
        storage = StorageService()
        watermark = storage.get_watermark(groupname)
    except Exception as e:
        print(f"加载 storage 或 watermark 失败: {e}")
        return

    try:
        with Spinner("LLM 分析中"):
            events = extractor.extract(messages, watermark)
    except Exception as e:
        print(f"AI 分析失败: {e}")
        return

    if not events:
        print("未提取到任何事件")
        return

    for event in events:
        print(event.print_Event())

    events = review_events(events)

    if not events:
        print("没有通过审查的事件")
        return

    print("\n以下为通过人工审查的 Event：")
    for event in events:
        print(event.print_Event())

    if not confirm(f"\n以上为 {len(events)} 个 Event，是否与日历同步？(y/n): "):
        print("已取消同步")
        return

    calendar = CalendarService(
        url=Config.CALDAV_URL,
        username=Config.CALDAV_USER,
        password=Config.CALDAV_PASS
    )

    if not calendar.connect():
        print("连接日历失败")
        return

    print(f"\n开始保存 {len(events)} 个事件到日历...")
    success_count = calendar.save_events_batch(events)
    print(f"完成！成功保存 {success_count}/{len(events)} 个事件")

    storage.update_watermark(groupname, messages[-1].timestamp)


def run_extract():
    """DDL 提取主入口 - 扫描 DATA_PATH 目录，按群名选择后逐文件处理"""
    if not Config.DEEPSEEK_API_KEY:
        Config.DEEPSEEK_API_KEY = Config.load_api_key_from_file('apikey.txt')

    if not Config.validate():
        return

    if not Config.DATA_PATH:
        print("错误：未设置 DATA_PATH，请在 .env 中指定聊天记录目录")
        return

    selected = _select_files(Config.DATA_PATH)
    if not selected:
        return

    print(f"\n已选择 {len(selected)} 个聊天记录")
    for entry in selected:
        _process_single_file(entry)

    print(f"\n{'='*50}")
    print("所有文件处理完毕")
