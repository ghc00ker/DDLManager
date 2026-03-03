"""本地状态管理 - 基于 JSON 文件的水位线和事件去重"""
import json
from datetime import datetime
from pathlib import Path
import sys
from typing import Optional, List
from ..models import Event


class StorageService:
    """JSON 文件存储
    
    状态文件结构：
    {
        "groups": [
            {
                "groupname": "群昵称（或者是群的唯一标识，与data中的对应，请勿擅自修改）",
                "watermark": "1751342496000",
                "processed_events": [
                    {"summary": "数据结构作业", "start_time": "2026-03-05T23:59:00"},
                    ...
                ]
            }
        ]
    }
    """

    def __init__(self, state_path: str = "ddlmanagerstates.json"):
        '''
        state_path是路径
        states是所有group的状态
        '''
        self.state_path = Path(state_path)
        self.states = self._load()

    def _load(self) -> dict:
        '''
        若ddlmanager.states.json存在则读取，否则报错
        '''
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            print("历史记录文件ddlmanagerstates.json不存在")
            sys.exit(1)
            # ？新建

    def _save(self):
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(self.states, f, ensure_ascii=False, indent=2)
            
    # 检索
    def get_group_index(self, groupname: str) -> int:
        """查找群组在列表中的索引"""
        for i, group in enumerate(self.states):
            if group.get("groupname") == groupname:
                return i
        return -1
    
    def get_group(self, groupname: str) -> dict:
        '''如果groups不存在，则新建'''
        index = self.get_group_index(groupname)
        if (index < 0):
            new_group= {
                "groupname": groupname,
                "watermark": None,
                "processed_events": []
            }
            self.states[groupname].append(new_group)
            return new_group
    # 水位线

    def get_watermark(self, groupname: str) -> Optional[datetime]:
        """获取上次处理到的最后一条消息的时间戳"""
        group = self.get_group(groupname)
        wm = self.states.get("watermark")
        if wm:
            return datetime.fromisoformat(wm)
        return None

    def update_watermark(self, groupname: str, timestamp: datetime):
        """更新水位线并持久化"""
        self.states["watermark"] = timestamp
        self._save()

    # 事件去重有爆大bug，summary可能不一样

    def is_duplicate(self, event: Event) -> bool:
        """检查是否已处理过相同的事件（按 summary + start_time 匹配）"""
        key = {
            "summary": event.summary,
            "start_time": event.start_datetime.isoformat()
        }
        return key in self.states["processed_events"]

    def record_event(self, event: Event):
        """记录已处理的事件（用于后续去重）"""
        key = {
            "summary": event.summary,
            "start_time": event.start_datetime.isoformat()
        }
        if key not in self.states["processed_events"]:
            self.states["processed_events"].append(key)
            self._save()

    def record_events(self, events: List[Event]):
        """批量记录"""
        for event in events:
            key = {
                "summary": event.summary,
                "start_time": event.start_datetime.isoformat()
            }
            if key not in self.states["processed_events"]:
                self.states["processed_events"].append(key)
        self._save()