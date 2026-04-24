"""
线索看板后端服务 v2
版本: 4.24.001
应用启动入口
"""
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app
from app.config import Config


def setup_logging():
    """配置日志"""
    log_dir = BASE_DIR / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'app.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def main():
    """主入口"""
    logger = setup_logging()
    
    # 创建应用
    app = create_app()
    
    print("=" * 50)
    print("🔐 线索看板服务 v2 启动中...")
    print(f"📍 访问地址: http://localhost:{Config.PORT}")
    print("=" * 50)
    print("\n测试账号：")
    print("  管理员: admin / admin123")
    print("  招商员1: zhengjianjun / zjj001345")
    print("  招商员2: liurenjie / lrj001678")
    print()
    
    logger.info(f"Starting server on port {Config.PORT}")
    
    app.run(
        debug=Config.DEBUG,
        host='0.0.0.0',
        port=Config.PORT,
        threaded=True
    )


if __name__ == '__main__':
    main()
