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
        self.states = self._load().get("groups")

    def _load(self) -> dict:
        '''若状态文件存在则读取，否则新建空结构'''
        if self.state_path.exists():
            with open(self.state_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        print(f"状态文件 {self.state_path} 不存在，已自动创建")
        empty = {"groups": []}
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(empty, f, ensure_ascii=False, indent=2)
        return empty

    def _save(self):
        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump({"groups": self.states}, f, ensure_ascii=False, indent=2)
            
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
            self.states.append(new_group)
            return new_group
        else:
            return self.states[index]
    # 水位线

    def get_watermark(self, groupname: str) -> Optional[datetime]:
        """获取上次处理到的最后一条消息的时间戳"""
        group = self.get_group(groupname)
        wm = group.get("watermark")
        if wm:
            return wm
        return datetime.min

    def update_watermark(self, groupname: str, timestamp: datetime):
        """更新水位线并持久化"""
        for state in self.states:
            if state.get("groupname") == groupname:
                state["watermark"] = timestamp.timestamp()
                break
        self._save()

    # 事件去重有爆大bug，summary可能不一样
