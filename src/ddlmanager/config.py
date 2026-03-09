"""配置管理 - 从环境变量读取敏感信息"""
import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Config:
    """应用配置（从环境变量读取）
    
    为什么用类而不是全局变量？
    - 可以创建多个配置实例（测试环境、生产环境）
    - 可以加入验证逻辑
    - 更容易做配置的继承和覆盖
    """
    
    # DeepSeek AI 配置
    DEEPSEEK_API_KEY: Optional[str] = os.getenv('DEEPSEEK_API_KEY')
    DEEPSEEK_BASE_URL: str = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
    
    # CalDAV 日历配置
    CALDAV_URL: Optional[str] = os.getenv('CALDAV_URL')
    CALDAV_USER: Optional[str] = os.getenv('CALDAV_USER')
    CALDAV_PASS: Optional[str] = os.getenv('CALDAV_PASS')
    
    # 文件地址
    DATA_PATH: Optional[str] = os.getenv('DATA_PATH')
    
    # 处理参数
    MAX_MESSAGES: int = int(os.getenv('MAX_MESSAGES', '5000'))
    CONTENT_NUM: int = int(os.getenv('CONTENT_NUM', '40'))
    
    @classmethod
    def validate(cls) -> bool:
        """验证必需的配置是否存在"""
        missing = []
        
        if not cls.DEEPSEEK_API_KEY:
            missing.append('DEEPSEEK_API_KEY')
        if not cls.CALDAV_URL:
            missing.append('CALDAV_URL')
        if not cls.CALDAV_USER:
            missing.append('CALDAV_USER')
        if not cls.CALDAV_PASS:
            missing.append('CALDAV_PASS')
        
        if missing:
            print(f"错误：缺少必需的环境变量: {', '.join(missing)}")
            print("请在 .env 文件或环境变量中设置这些配置")
            return False
        
        return True
    
    @classmethod
    def load_api_key_from_file(cls, filepath: str = 'apikey.txt') -> Optional[str]:
        """从文件读取 API Key（仅用于本地开发）
        
        注意：这是临时方案，生产环境应使用环境变量
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                if lines:
                    return lines[0]
        except FileNotFoundError:
            pass
        return None
