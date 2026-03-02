# 迁移指南：从 main.py 到模块化结构

## 一、快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：
```
DEEPSEEK_API_KEY=sk-你的密钥
CALDAV_URL=https://dav.qq.com
CALDAV_USER=你的邮箱@qq.com
CALDAV_PASS=你的CalDAV密码
```

### 3. 运行新版本

```bash
# 方式 1: 直接运行（推荐）
python -m src.ddlmanager.cli

# 方式 2: 指定输入文件
python -m src.ddlmanager.cli data/your_chat_export.json
```

## 二、新旧对比

### 旧版本（main.py）

```python
# 所有代码混在一起，不易维护
def main():
    # 硬编码的密码 😱
    password = "vxwkkfcsoiyodjca"
    # 解析、AI、日历操作全在一个函数里
    ...
```

### 新版本（模块化）

```python
# cli.py - 清晰的流程编排
from ddlmanager.parsers import QQParser
from ddlmanager.services import AIClient, DDLExtractor, CalendarService
from ddlmanager.config import Config

parser = QQParser()
messages = parser.parse(input_path)

extractor = DDLExtractor(AIClient(...))
events = extractor.extract(messages)

calendar = CalendarService(...)
calendar.save_events_batch(events)
```

## 三、`__init__.py` 详解（教学）

### 什么是 `__init__.py`？

在 Python 中，一个包含 `__init__.py` 的文件夹会被视为一个**包（Package）**。

### 三种写法

#### 1. 空文件（最简单）

```python
# models/__init__.py
# 空的，只标记这是一个包
```

使用时：
```python
from ddlmanager.models.message import Message  # 必须写完整路径
```

#### 2. 重新导出（推荐 ⭐）

```python
# models/__init__.py
from .message import Message
from .event import Event

__all__ = ['Message', 'Event']
```

使用时：
```python
from ddlmanager.models import Message, Event  # 简洁！
```

**好处**：
- 外部调用者不需要知道内部文件结构
- 可以随意重构内部文件，不影响外部接口
- IDE 自动补全更友好

#### 3. 包级初始化（少用）

```python
# __init__.py
print("包被导入时执行")
GLOBAL_CONFIG = load_config()  # 不推荐，有副作用
```

### `__all__` 的作用

```python
__all__ = ['Message', 'Event']
```

作用：
- 控制 `from package import *` 时导入哪些名称
- 明确标记"公开 API"（给其他人用的）
- 即使不用 `import *`，`__all__` 也有文档作用

## 四、新结构的优势

### 1. 职责分离
- `models/`: 只定义数据结构
- `parsers/`: 只负责解析输入
- `services/`: 只封装外部服务（AI、日历）
- `cli.py`: 只编排流程

### 2. 易于测试

```python
# tests/test_parser.py
from ddlmanager.parsers import QQParser

def test_parse_qq_message():
    parser = QQParser()
    messages = parser.parse({'messages': [...]})
    assert len(messages) > 0
```

### 3. 易于扩展

需要支持微信？只需：
```python
# parsers/wechat_parser.py
class WeChatParser(MessageParser):
    def parse(self, source):
        # 实现微信解析逻辑
        ...
```

然后在 `parsers/__init__.py` 加一行：
```python
from .wechat_parser import WeChatParser
```

## 五、验证新结构

运行测试验证导入是否正常：

```bash
python tests/test_structure.py
```

应该看到：
```
✓ 所有子包导入成功
✓ 顶层包导入成功
✓ 版本号: 0.1.0
```

## 六、下一步

1. ✅ 已完成：模块化重构
2. 📝 待办：将 `main.py` 中的敏感信息移到 `.env`
3. 📝 待办：运行一次完整测试，确保功能正常
4. 📝 待办：（可选）添加更多解析器（微信、文本等）
