/**
 * 用户管理路由（仅管理员）
 */
const express = require('express');
const db = require('../db');
const { requireAdmin } = require('../middleware/auth');

const router = express.Router();

// GET /api/users
router.get('/api/users', requireAdmin, (req, res) => {
  const rows = db.prepare('SELECT id, username, name, role, regions, active, must_change_password, created_at FROM users ORDER BY role, created_at').all();
  const users = rows.map(r => ({
    ...r,
    regions: r.regions ? JSON.parse(r.regions) : [],
  }));
  res.json({ success: true, users });
});

// POST /api/users
router.post('/api/users', requireAdmin, (req, res) => {
  const { username, name, role, regions } = req.body;
  const u = (username || '').trim().toLowerCase();
  const n = (name || '').trim();
  const r = (role || 'agent').trim();

  if (!u || !n) {
    return res.json({ success: false, message: '用户名和姓名不能为空' });
  }
  if (!/^[a-z0-9]+$/.test(u)) {
    return res.json({ success: false, message: '用户名只能包含英文和数字' });
  }

  const validRoles = ['admin', 'agent', 'guest'];
  if (!validRoles.includes(r)) {
    return res.json({ success: false, message: '角色无效，可选：admin、agent、guest' });
  }

  const existing = db.prepare('SELECT id FROM users WHERE username = ?').get(u);
  if (existing) {
    return res.json({ success: false, message: '用户名已存在' });
  }

  const now = new Date().toISOString().replace('T', ' ').slice(0, 19);
  const regionsJson = Array.isArray(regions) ? JSON.stringify(regions) : '[]';

  db.prepare(`INSERT INTO users (username, password, name, role, regions, active, must_change_password, created_at)
    VALUES (?, ?, ?, ?, ?, 1, 1, ?)`)
    .run(u, '123456', n, r, regionsJson, now);

  res.json({ success: true, message: '账号创建成功，初始密码：123456' });
});

// POST /api/users/toggle
router.post('/api/users/toggle', requireAdmin, (req, res) => {
  const { id } = req.body;
  if (!id) {
    return res.json({ success: false, message: '缺少用户ID' });
  }

  const user = db.prepare('SELECT active, role FROM users WHERE id = ?').get(id);
  if (!user) {
    return res.json({ success: false, message: '用户不存在' });
  }
  if (user.role === 'admin') {
    return res.json({ success: false, message: '不能停用管理员账号' });
  }

  const newActive = user.active ? 0 : 1;
  db.prepare('UPDATE users SET active = ? WHERE id = ?').run(newActive, id);

  res.json({ success: true, message: newActive ? '账号已启用' : '账号已停用', active: newActive });
});

// POST /api/users/delete
router.post('/api/users/delete', requireAdmin, (req, res) => {
  const { id } = req.body;
  if (!id) {
    return res.json({ success: false, message: '缺少用户ID' });
  }

  const user = db.prepare('SELECT role FROM users WHERE id = ?').get(id);
  if (!user) {
    return res.json({ success: false, message: '用户不存在' });
  }
  if (user.role === 'admin') {
    return res.json({ success: false, message: '不能删除管理员账号' });
  }

  db.prepare('DELETE FROM users WHERE id = ?').run(id);
  res.json({ success: true, message: '账号已删除' });
});

module.exports = router;
