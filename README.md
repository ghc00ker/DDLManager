## 📅 iCalendar Event 常用字段一览表

| 字段名 | 含义 | 是否必需 | 代码示例 |
|--------|------|----------|----------|
| **`uid`** | 唯一标识符 | **是** | `event.add('uid', '20240601-1234@example.com')` |
| **`dtstamp`** | 创建时间戳 | **是** | `event.add('dtstamp', datetime.now())` |
| **`dtstart`** | 开始时间 | **是** | `event.add('dtstart', datetime(2024, 6, 1, 10, 0))` |
| **`dtend`** | 结束时间 | 与`duration`二选一 | `event.add('dtend', datetime(2024, 6, 1, 11, 0))` |
| **`duration`** | 持续时间 | 与`dtend`二选一 | `event.add('duration', timedelta(hours=2))` |
| **`summary`** | 事件主题/标题 | 推荐 | `event.add('summary', '团队周会')` |
| **`description`** | 详细描述 | 否 | `event.add('description', '同步本周工作进展')` |
| **`location`** | 地点 | 否 | `event.add('location', '会议室A / Zoom链接')` |
| **`attendee`** | 参会人 | 否 | `event.add('attendee', 'mailto:zhang@example.com')` |
| **`organizer`** | 组织者 | 否 | `event.add('organizer', 'mailto:me@example.com')` |
| **`rrule`** | 重复规则 | 否 | `event.add('rrule', {'freq': 'weekly', 'interval': 1})` |
| **`status`** | 事件状态 | 否 | `event.add('status', 'CONFIRMED')` |
| **`priority`** | 优先级 | 否 | `event.add('priority', 5)` |
| **`categories`** | 分类标签 | 否 | `event.add('categories', ['工作', '重要会议'])` |
| **`class`** | 访问权限 | 否 | `event.add('class', 'PUBLIC')` |
| **`transp`** | 忙碌状态 | 否 | `event.add('transp', 'OPAQUE')` |
| **`url`** | 关联链接 | 否 | `event.add('url', 'https://meeting.zoom.com/123')` |
| **`created`** | 创建时间 | 否 | `event.add('created', datetime(2024, 5, 1, 9, 0))` |
| **`last-modified`** | 最后修改时间 | 否 | `event.add('last-modified', datetime.now())` |
| **`sequence`** | 版本序列号 | 否 | `event.add('sequence', 1)` |

## 📌 字段说明补充

### **必需字段详解**
- **`uid`**：全局唯一，用于更新/删除时定位事件。格式建议：`<日期>-<随机字符串>@<域名>`
- **`dtstamp`**：代表这个iCalendar数据的创建时刻，不是事件的开始时间
- **`dtstart`**：事件的开始时间，可以带时区：`event.add('dtstart', datetime(2024, 6, 1, 10, 0, tzinfo=zoneinfo.ZoneInfo('Asia/Shanghai')))`

### **状态字段取值**
| 字段 | 可选值 | 说明 |
|------|--------|------|
| **`status`** | `TENTATIVE` / `CONFIRMED` / `CANCELLED` | 事件状态 |
| **`class`** | `PUBLIC` / `PRIVATE` / `CONFIDENTIAL` | 访问权限 |
| **`transp`** | `OPAQUE` / `TRANSPARENT` | OPAQUE表示忙碌，TRANSPARENT表示空闲 |
| **`priority`** | 1-9 | 1最高，9最低 |

### **参会人示例（带参数）**
```python
from icalendar import vCalAddress

attendee = vCalAddress('mailto:wang@example.com')
attendee.params['cn'] = '王小明'           # 显示名称
attendee.params['role'] = 'REQ-PARTICIPANT'  # 必需参会
attendee.params['partstat'] = 'NEEDS-ACTION' # 待确认
attendee.params['rsvp'] = 'TRUE'             # 需要回复
event.add('attendee', attendee)
```

### **重复规则示例**
```python
# 每周一、三、五，共10次
event.add('rrule', {
    'freq': 'weekly',
    'byday': ['mo', 'we', 'fr'],
    'count': 10
})

# 每月最后一个周五，无限重复
event.add('rrule', {
    'freq': 'monthly',
    'byday': 'fr',
    'bysetpos': -1  # 最后一个
})

# 每天，直到年底
event.add('rrule', {
    'freq': 'daily',
    'until': datetime(2024, 12, 31)
})
```

该项目通过Caldav进行日程管理，通过本地的聊天记录和LLM进行分析


分析

问题：平时群太多，容易看漏东西，比如课程作业安排，作业改动，考试安排，学院通知等等。

同类项目：

    元宝总结：和QQ深度融合，格式规范，可以标签指引到相关对话与图片，方便用户亲自确认信息，但是微信没有相关功能
    WeFlow：github开源项目可能可以有方便的接口，只有统计功能不能分析

功能（重要性递减）：

    能将QQ群聊（对话）的聊天记录分析并且总结重要事项
    能将微信群聊（对话）的聊天记录分析并且总结重要事项（微信更难获取聊天记录）
    能够分析出Deadline并且按照时间排序
    能够通过手机自带的日历进行自动安排
    能够部署云端
    能够通过类似公众号（我试过相关TODO list产品）来提醒

技术：

    读取QQ群聊消息
    deepseek/qwen api分析消息
    读取微信群聊消息（最难）
    根据格式输出内容
    根据手机日历api进行写入日程
    云端部署