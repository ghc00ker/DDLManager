"""入口脚本 - 运行 DDLManager 交互式菜单

使用方式：
    python run.py
"""
import sys
from pathlib import Path

# 添加 src 到 Python 路径
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

# 导入并运行
from ddlmanager.cli import main

if __name__ == '__main__':
    main()
