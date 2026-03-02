"""命令行入口 - 主流程编排"""
import sys
from pathlib import Path
from .config import Config
from .parsers import QQParser
from .services import AIClient, CalendarService, DDLExtractor
from .models import Event


def main():
    """主流程：读取聊天记录 -> AI 分析 -> 保存到日历
    
    流程设计原则：
    1. 快速失败（配置验证）
    2. 职责分离（每个步骤调用对应的服务）
    3. 清晰的错误提示
    """
    
    # 1. 配置验证
    if not Config.DEEPSEEK_API_KEY:
        Config.DEEPSEEK_API_KEY = Config.load_api_key_from_file('apikey.txt')
    
    if not Config.validate():
        sys.exit(1)
    
    # 2. 读取输入文件
    input_path = sys.argv[1] if len(sys.argv) > 1 else 'data/group_792340423_20260223_230254.json'
    
    if not Path(input_path).exists():
        print(f'错误：文件不存在 {input_path}')
        sys.exit(1)
    
    print(f"正在读取: {input_path}")
    
    # 3. 解析消息
    parser = QQParser()
    try:
        messages = parser.parse(input_path)
        print(f"已解析 {len(messages)} 条消息")
    except Exception as e:
        print(f'解析消息失败: {e}')
        sys.exit(1)
    
    if not messages:
        print('没有找到有效消息')
        sys.exit(0)
    
    # 4. AI 提取 DDL
    ai_client = AIClient(
        api_key=Config.DEEPSEEK_API_KEY,
        base_url=Config.DEEPSEEK_BASE_URL
    )
    extractor = DDLExtractor(ai_client)
    
    try:
        events = extractor.extract(messages, max_messages=Config.MAX_MESSAGES)
    except Exception as e:
        print(f'AI 分析失败: {e}')
        sys.exit(1)
    
    if not events:
        print('未提取到任何事件')
        sys.exit(0)
    
    # 5. 保存到日历
    calendar = CalendarService(
        url=Config.CALDAV_URL,
        username=Config.CALDAV_USER,
        password=Config.CALDAV_PASS
    )
    
    if not calendar.connect():
        print('连接日历失败')
        sys.exit(1)
    
    print(f"\n开始保存 {len(events)} 个事件到日历...")
    success_count = calendar.save_events_batch(events)
    
    print(f"\n完成！成功保存 {success_count}/{len(events)} 个事件")


if __name__ == '__main__':
    main()
