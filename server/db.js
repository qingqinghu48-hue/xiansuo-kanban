/**
 * 数据库连接和初始化
 * 使用 better-sqlite3（同步 API）
 */
const Database = require('better-sqlite3');
const path = require('path');
const crypto = require('crypto');
const { formatDateTime } = require('./utils/helpers');

const DB_FILE = path.join(__dirname, '..', 'leads.db');

const db = new Database(DB_FILE);

/**
 * 密码哈希工具
 */
function hashPassword(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const hash = crypto.scryptSync(password, salt, 32).toString('hex');
  return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
  if (!stored || !stored.includes(':')) return false;
  const [salt, hash] = stored.split(':');
  const computed = crypto.scryptSync(password, salt, 32).toString('hex');
  return computed === hash;
}

/**
 * 将现有明文密码迁移为哈希存储
 */
function migratePasswords() {
  try {
    const rows = db.prepare("SELECT id, password FROM users WHERE password IS NOT NULL AND password NOT LIKE '%:%'").all();
    if (!rows.length) return;
    const stmt = db.prepare('UPDATE users SET password = ? WHERE id = ?');
    for (const row of rows) {
      stmt.run(hashPassword(row.password), row.id);
      console.log(`[密码迁移] 用户ID ${row.id} 密码已哈希化`);
    }
    console.log(`[密码迁移] 共迁移 ${rows.length} 个用户的明文密码`);
  } catch (e) {
    console.log('[密码迁移] 失败:', e.message);
  }
}

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
    // 招商线索管理表新增字段
    { name: 'is_duplicate', type: 'TEXT DEFAULT ""' },
    // 小红书线索列表数据新增字段
    { name: 'xhs_nickname', type: 'TEXT DEFAULT ""' },
    { name: 'xhs_user_id', type: 'TEXT DEFAULT ""' },
    { name: 'xhs_uid', type: 'TEXT DEFAULT ""' },
    { name: 'source_note', type: 'TEXT DEFAULT ""' },
    { name: 'creative_name', type: 'TEXT DEFAULT ""' },
    { name: 'creative_id', type: 'TEXT DEFAULT ""' },
    { name: 'conversion_method', type: 'TEXT DEFAULT ""' },
    { name: 'wechat_id', type: 'TEXT DEFAULT ""' },
    { name: 'detail_json', type: 'TEXT DEFAULT ""' },
    // 抖音客资中心新增字段
    { name: 'intention_type', type: 'TEXT DEFAULT ""' },
    { name: 'intention_store', type: 'TEXT DEFAULT ""' },
    { name: 'intention_store_id', type: 'TEXT DEFAULT ""' },
    { name: 'follow_up_account', type: 'TEXT DEFAULT ""' },
    { name: 'latest_follow_note', type: 'TEXT DEFAULT ""' },
    { name: 'lead_stage', type: 'TEXT DEFAULT ""' },
    { name: 'lead_tags', type: 'TEXT DEFAULT ""' },
    { name: 'call_count', type: 'INTEGER DEFAULT 0' },
    { name: 'marketing_type', type: 'TEXT DEFAULT ""' },
    { name: 'last_call_time', type: 'TEXT DEFAULT ""' },
    { name: 'smart_intention', type: 'TEXT DEFAULT ""' },
    { name: 'interaction_scene', type: 'TEXT DEFAULT ""' },
    { name: 'latest_lead_record', type: 'TEXT DEFAULT ""' },
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

  // 创建 users 表（替代 YAML）
  db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      name TEXT NOT NULL,
      role TEXT NOT NULL,
      regions TEXT DEFAULT '',
      active INTEGER DEFAULT 1,
      must_change_password INTEGER DEFAULT 0,
      created_at TEXT NOT NULL
    )
  `);

  // 创建 platforms 表
  db.exec(`
    CREATE TABLE IF NOT EXISTS platforms (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      sort_order INTEGER DEFAULT 0,
      created_at TEXT NOT NULL
    )
  `);

  // 创建 regions 表
  db.exec(`
    CREATE TABLE IF NOT EXISTS regions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT UNIQUE NOT NULL,
      created_at TEXT NOT NULL
    )
  `);

  // 创建常用查询索引
  db.exec(`CREATE INDEX IF NOT EXISTS idx_new_leads_platform ON new_leads(platform)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_new_leads_agent ON new_leads(agent)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_new_leads_entry_date ON new_leads(entry_date)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_new_leads_is_read ON new_leads(is_read)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_new_leads_created_at ON new_leads(created_at)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_cost_data_cost_date ON cost_data(cost_date)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_cost_data_platform ON cost_data(platform)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)`);
  db.exec(`CREATE INDEX IF NOT EXISTS idx_users_active ON users(active)`);
}

/**
 * 从 YAML 迁移用户数据到 SQLite（只执行一次）
 */
function migrateUsersFromYaml() {
  try {
    const yaml = require('js-yaml');
    const fs = require('fs');
    const path = require('path');
    const yamlFile = path.join(__dirname, '..', 'users.yaml');
    if (!fs.existsSync(yamlFile)) return;

    const count = db.prepare('SELECT COUNT(*) as cnt FROM users').get().cnt;
    if (count > 0) return; // 已有数据，跳过

    const data = yaml.load(fs.readFileSync(yamlFile, 'utf-8'));
    const now = formatDateTime();
    const stmt = db.prepare(`INSERT INTO users (username, password, name, role, regions, active, must_change_password, created_at)
      VALUES (?, ?, ?, ?, ?, 1, 0, ?)`);

    if (data.admin) {
      stmt.run(data.admin.username, data.admin.password, data.admin.name, 'admin', '', now);
    }
    for (const agent of data.agents || []) {
      stmt.run(agent.username, agent.password, agent.name, 'agent', JSON.stringify(agent.regions || []), now);
    }
    if (data.guest) {
      stmt.run(data.guest.username, data.guest.password, data.guest.name, 'guest', '', now);
    }
    console.log('[迁移] users.yaml 数据已导入 SQLite');
  } catch (e) {
    console.log('[迁移] 用户迁移失败:', e.message);
  }
}

/**
 * 初始化默认平台来源
 */
function initPlatforms() {
  const count = db.prepare('SELECT COUNT(*) as cnt FROM platforms').get().cnt;
  if (count > 0) return;
  const now = formatDateTime();
  const stmt = db.prepare('INSERT INTO platforms (name, sort_order, created_at) VALUES (?, ?, ?)');
  const defaults = ['抖音', '小红书', '豆包', '400线索', '品专', '转介绍'];
  defaults.forEach((name, i) => stmt.run(name, i, now));
  console.log('[初始化] 默认平台来源已创建');
}

function initRegions() {
  const now = formatDateTime();
  const standardRegions = ['上海区域', '常锡区域', '其他区域', '南京区域', '深莞惠区域', '苏州区域', '镇扬泰区域'];

  // 1. 清洗 regions 表：删除非标准区域（组合区域）
  const allRegions = db.prepare('SELECT name FROM regions').all();
  for (const row of allRegions) {
    if (!standardRegions.includes(row.name)) {
      db.prepare('DELETE FROM regions WHERE name = ?').run(row.name);
      console.log(`[清洗] 删除组合区域: ${row.name}`);
    }
  }

  // 2. 确保标准区域都存在
  const stmt = db.prepare('INSERT OR IGNORE INTO regions (name, created_at) VALUES (?, ?)');
  for (const name of standardRegions) {
    stmt.run(name, now);
  }

  // 3. 规范化 new_leads 的 region 字段：统一分隔符为 ", "
  const leads = db.prepare("SELECT id, region FROM new_leads WHERE region IS NOT NULL AND region != ''").all();
  const updateStmt = db.prepare('UPDATE new_leads SET region = ? WHERE id = ?');
  let normalizedCount = 0;
  for (const lead of leads) {
    const normalized = String(lead.region).split(/[,，、]\s*/).map(s => s.trim()).filter(Boolean).join(', ');
    if (normalized !== lead.region) {
      updateStmt.run(normalized, lead.id);
      normalizedCount++;
    }
  }
  if (normalizedCount > 0) {
    console.log(`[清洗] 已规范化 ${normalizedCount} 条线索的 region 字段`);
  }
}

function fixPlatformClassification() {
  try {
    const mappings = [
      { from: '抖音广告', to: '抖音' },
      { from: '抖音自然流', to: '抖音' },
      { from: '小红书广告', to: '小红书' },
      { from: '自媒体小红书', to: '小红书' },
    ];
    for (const { from, to } of mappings) {
      const row = db.prepare("SELECT COUNT(*) as cnt FROM new_leads WHERE platform = ?").get(from);
      if (row && row.cnt > 0) {
        db.prepare("UPDATE new_leads SET platform = ? WHERE platform = ?").run(to, from);
        console.log(`[启动修复] 已将 ${row.cnt} 条'${from}'改为'${to}'`);
      }
    }
  } catch (e) {
    console.log(`[启动修复] 修复平台分类失败: ${e.message}`);
  }
}

initDb();
fixPlatformClassification();
migrateUsersFromYaml();
initPlatforms();
initRegions();
migratePasswords();

module.exports = db;
module.exports.hashPassword = hashPassword;
module.exports.verifyPassword = verifyPassword;
