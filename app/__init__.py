"""
线索看板 - Flask 应用工厂
"""
import os
from flask import Flask

from .config import Config
from .models import init_db, fix_platform_classification


def create_app(config_class=Config):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 设置密钥
    app.secret_key = config_class.SECRET_KEY

    # 初始化数据库
    init_db()
    fix_platform_classification()

    # 注册蓝图（按需导入，避免模块缺失导致启动失败）
    blueprints = [
        ('app.routes.auth', 'auth_bp'),
        ('app.routes.leads', 'leads_bp'),
        ('app.routes.cost', 'cost_bp'),
        ('app.routes.notifications', 'notifications_bp'),
        ('app.routes.pages', 'pages_bp'),
    ]
    for module_name, bp_name in blueprints:
        try:
            module = __import__(module_name, fromlist=[bp_name])
            bp = getattr(module, bp_name)
            app.register_blueprint(bp)
        except (ImportError, AttributeError) as e:
            print(f"[WARN] 蓝图 {bp_name} 注册失败: {e}")
            pass

    return app
