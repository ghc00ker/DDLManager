"""结构验证测试 - 确保模块可以正确导入"""
import sys
from pathlib import Path

# Windows 控制台 UTF-8 支持
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


def test_imports():
    """测试所有核心类是否可以正常导入"""
    try:
        # 测试从子包导入
        from ddlmanager.models import Message, Event
        from ddlmanager.parsers import QQParser, MessageParser
        from ddlmanager.services import AIClient, CalendarService, DDLExtractor
        from ddlmanager.config import Config
        
        print("✓ 所有子包导入成功")
        
        # 测试从顶层包导入
        from ddlmanager import Message, Event, QQParser, Config
        
        print("✓ 顶层包导入成功")
        
        # 测试版本号
        import ddlmanager
        print(f"✓ 版本号: {ddlmanager.__version__}")
        
        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


if __name__ == '__main__':
    success = test_imports()
    sys.exit(0 if success else 1)
