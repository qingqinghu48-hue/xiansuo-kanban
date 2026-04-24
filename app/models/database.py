"""
数据库连接管理
"""
import sqlite3

from ..config import Config


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(str(Config.DB_FILE))
    return conn


def init_db():
    """数据库初始化（包含所有 CREATE TABLE 和 ALTER TABLE）"""
    conn = sqlite3.connect(str(Config.DB_FILE))
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS new_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            platform TEXT NOT NULL,
            agent TEXT NOT NULL,
            entry_date TEXT DEFAULT '',
            name TEXT DEFAULT '',
            city TEXT DEFAULT '',
            validity TEXT DEFAULT '',
            region TEXT DEFAULT '',
            can_wechat TEXT DEFAULT '',
            remark TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            xhs_account TEXT DEFAULT '',
            lead_type TEXT DEFAULT '',
            UNIQUE(phone)
        )
    ''')
    # 添加新字段（如果不存在）
    try:
        c.execute('ALTER TABLE new_leads ADD COLUMN xhs_account TEXT DEFAULT ""')
    except sqlite3.OperationalError:
        pass
    try:
        c.execute('ALTER TABLE new_leads ADD COLUMN lead_type TEXT DEFAULT ""')
    except sqlite3.OperationalError:
        pass
    conn.commit()
    # 线索成本表
    c.execute('''
        CREATE TABLE IF NOT EXISTS cost_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cost_date TEXT NOT NULL,
            platform TEXT NOT NULL,
            amount REAL NOT NULL,
            unit_cost REAL DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(cost_date, platform)
        )
    ''')
    # 兼容旧表：若缺少 unit_cost 列则添加
    try:
        c.execute('SELECT unit_cost FROM cost_data LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE cost_data ADD COLUMN unit_cost REAL DEFAULT 0')
    conn.commit()
    conn.close()


def fix_platform_classification():
    """启动时将'抖音广告'改为'抖音'"""
    try:
        conn = sqlite3.connect(str(Config.DB_FILE))
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM new_leads WHERE platform = '抖音广告'")
        count = c.fetchone()[0]
        if count > 0:
            c.execute("UPDATE new_leads SET platform = '抖音' WHERE platform = '抖音广告'")
            conn.commit()
            print(f"[启动修复] 已将 {count} 条'抖音广告'改为'抖音'")
        conn.close()
    except Exception as e:
        print(f"[启动修复] 修复平台分类失败: {e}")
