"""
配置管理
从环境变量和 .env 文件读取配置
参考 SupplyChainSystem 风格
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# 加载 .env 文件（若 python-dotenv 可用）
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=str(env_path))
except ImportError:
    pass


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'xiansuo-kanban-secret-key-2024')
    PORT = int(os.getenv('PORT', '5001'))
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')
    BASE_DIR = BASE_DIR
    USERS_FILE = BASE_DIR / 'users.yaml'
    DATA_FILE = BASE_DIR / 'dashboard_data.json'
    DB_FILE = BASE_DIR / 'leads.db'
