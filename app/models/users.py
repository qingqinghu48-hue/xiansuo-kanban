"""
用户模型
"""
import yaml

from ..config import Config


def load_users():
    """加载 users.yaml"""
    with open(Config.USERS_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
