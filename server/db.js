/**
 * 数据库连接和初始化
 * 使用 better-sqlite3（同步 API）
 */
const Database = require('better-sqlite3');
const path = require('path');

const DB_FILE = path.join(__dirname, '..', 'leads.db');

const db = new Database(DB_FILE);

function initDb() {
  // 创建 new_leads 表
  db.exec(`
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
  `);

  // 添加可能缺失的字段（兼容旧表）
  const columns = db.prepare("PRAGMA table_info(new_leads)").all();
  const colNames = columns.map(c => c.name);

  const missingCols = [
    { name: 'xhs_account', type: 'TEXT DEFAULT ""' },
    { name: 'lead_type', type: 'TEXT DEFAULT ""' },
    { name: '二次联系时间', type: 'TEXT DEFAULT ""' },
    { name: '二次联系备注', type: 'TEXT DEFAULT ""' },
    { name: '最近一次电联时间', type: 'TEXT DEFAULT ""' },
    { name: '到访时间', type: 'TEXT DEFAULT ""' },
    { name: '签约时间', type: 'TEXT DEFAULT ""' },
  ];

  for (const col of missingCols) {
    if (!colNames.includes(col.name)) {
      try {
        db.exec(`ALTER TABLE new_leads ADD COLUMN ${col.name} ${col.type}`);
      } catch (e) {
        // 忽略错误
      }
    }
  }

  // 创建 cost_data 表
  db.exec(`
    CREATE TABLE IF NOT EXISTS cost_data (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cost_date TEXT NOT NULL,
      platform TEXT NOT NULL,
      amount REAL NOT NULL,
      unit_cost REAL DEFAULT 0,
      created_at TEXT NOT NULL,
      UNIQUE(cost_date, platform)
    )
  `);

  // 兼容旧表：若缺少 unit_cost 列则添加
  const costColumns = db.prepare("PRAGMA table_info(cost_data)").all();
  const costColNames = costColumns.map(c => c.name);
  if (!costColNames.includes('unit_cost')) {
    try {
      db.exec('ALTER TABLE cost_data ADD COLUMN unit_cost REAL DEFAULT 0');
    } catch (e) {
      // 忽略错误
    }
  }
}

function fixPlatformClassification() {
  try {
    const row = db.prepare("SELECT COUNT(*) as cnt FROM new_leads WHERE platform = '抖音广告'").get();
    if (row && row.cnt > 0) {
      db.exec("UPDATE new_leads SET platform = '抖音' WHERE platform = '抖音广告'");
      console.log(`[启动修复] 已将 ${row.cnt} 条'抖音广告'改为'抖音'`);
    }
  } catch (e) {
    console.log(`[启动修复] 修复平台分类失败: ${e.message}`);
  }
}

initDb();
fixPlatformClassification();

module.exports = db;
