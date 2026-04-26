/**
 * 基于 better-sqlite3 的 Session Store
 * 实现 express-session Store 接口，session 持久化到 SQLite
 */
const { Store } = require('express-session');

class SqliteSessionStore extends Store {
  constructor(db, options = {}) {
    super(options);
    this.db = db;
    this.tableName = options.tableName || 'sessions';
    this.initTable();
  }

  initTable() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS ${this.tableName} (
        sid TEXT PRIMARY KEY,
        sess TEXT NOT NULL,
        expire INTEGER NOT NULL
      )
    `);
    // 创建过期时间索引，便于清理
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_${this.tableName}_expire ON ${this.tableName}(expire)`);
  }

  get(sid, callback) {
    try {
      const now = Date.now();
      const row = this.db.prepare(
        `SELECT sess FROM ${this.tableName} WHERE sid = ? AND expire > ?`
      ).get(sid, now);
      if (!row) return callback(null, null);
      const sess = JSON.parse(row.sess);
      callback(null, sess);
    } catch (e) {
      callback(e);
    }
  }

  set(sid, sess, callback) {
    try {
      const now = Date.now();
      // maxAge 是毫秒，如果 sess.cookie 存在就取它，否则默认 14 天
      const maxAge = (sess.cookie && sess.cookie.maxAge) || (14 * 24 * 60 * 60 * 1000);
      const expire = now + maxAge;
      const sessStr = JSON.stringify(sess);
      this.db.prepare(
        `INSERT INTO ${this.tableName} (sid, sess, expire) VALUES (?, ?, ?)
         ON CONFLICT(sid) DO UPDATE SET sess = excluded.sess, expire = excluded.expire`
      ).run(sid, sessStr, expire);
      callback && callback(null);
    } catch (e) {
      callback && callback(e);
    }
  }

  destroy(sid, callback) {
    try {
      this.db.prepare(`DELETE FROM ${this.tableName} WHERE sid = ?`).run(sid);
      callback && callback(null);
    } catch (e) {
      callback && callback(e);
    }
  }

  touch(sid, sess, callback) {
    // 更新过期时间
    try {
      const now = Date.now();
      const maxAge = (sess.cookie && sess.cookie.maxAge) || (14 * 24 * 60 * 60 * 1000);
      const expire = now + maxAge;
      this.db.prepare(
        `UPDATE ${this.tableName} SET expire = ? WHERE sid = ?`
      ).run(expire, sid);
      callback && callback(null);
    } catch (e) {
      callback && callback(e);
    }
  }

  // 清理过期 session
  gc() {
    try {
      const result = this.db.prepare(
        `DELETE FROM ${this.tableName} WHERE expire < ?`
      ).run(Date.now());
      if (result.changes > 0) {
        console.log(`[Session GC] 清理 ${result.changes} 个过期 session`);
      }
    } catch (e) {
      console.error('[Session GC] 失败:', e.message);
    }
  }
}

module.exports = SqliteSessionStore;
