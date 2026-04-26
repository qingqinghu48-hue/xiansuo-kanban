/**
 * 认证路由
 */
const express = require('express');
const db = require('../db');
const { verifyPassword, hashPassword } = require('../db');
const { validateSessionUser } = require('../middleware/auth');

const router = express.Router();

function loadUserByUsername(username) {
  return db.prepare('SELECT * FROM users WHERE username = ?').get(username);
}

// POST /api/login
router.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  const u = (username || '').trim();
  const p = (password || '').trim();

  if (!u || !p) {
    return res.json({ success: false, message: '请输入用户名和密码' });
  }

  const user = loadUserByUsername(u);
  if (!user) {
    return res.json({ success: false, message: '用户名或密码错误' });
  }

  if (!user.active) {
    return res.json({ success: false, message: '账号已停用，请联系管理员' });
  }

  if (!verifyPassword(p, user.password)) {
    return res.json({ success: false, message: '用户名或密码错误' });
  }

  const sessionUser = {
    id: user.id,
    username: user.username,
    name: user.name,
    role: user.role,
    regions: user.regions ? JSON.parse(user.regions) : [],
    must_change_password: user.must_change_password,
  };

  req.session.user = sessionUser;

  return res.json({
    success: true,
    name: user.name,
    role: user.role,
    must_change_password: user.must_change_password,
  });
});

// POST /api/logout
router.post('/api/logout', (req, res) => {
  req.session.destroy(() => {});
  res.json({ success: true });
});

// GET /api/current_user
router.get('/api/current_user', (req, res) => {
  const user = req.session ? req.session.user : null;
  if (!user) {
    return res.json({ logged_in: false });
  }
  if (!validateSessionUser(req, res)) {
    return res.json({ logged_in: false });
  }
  return res.json({ logged_in: true, user });
});

// POST /api/change-password
router.post('/api/change-password', (req, res) => {
  const user = req.session ? req.session.user : null;
  if (!user) {
    return res.status(401).json({ success: false, message: '请先登录' });
  }
  if (!validateSessionUser(req, res)) {
    return res.status(401).json({ success: false, message: '登录已失效，请重新登录' });
  }

  const { old_password, new_password } = req.body;
  const oldP = (old_password || '').trim();
  const newP = (new_password || '').trim();

  if (!newP) {
    return res.json({ success: false, message: '请输入新密码' });
  }
  if (newP.length !== 6) {
    return res.json({ success: false, message: '密码必须为6位' });
  }

  const dbUser = db.prepare('SELECT * FROM users WHERE id = ?').get(user.id);
  if (!dbUser) {
    return res.json({ success: false, message: '用户不存在' });
  }

  // 首次登录时 old_password 传空，不用校验旧密码
  if (dbUser.must_change_password === 0 && !verifyPassword(oldP, dbUser.password)) {
    return res.json({ success: false, message: '旧密码错误' });
  }

  db.prepare('UPDATE users SET password = ?, must_change_password = 0 WHERE id = ?')
    .run(hashPassword(newP), user.id);

  // 更新 session
  req.session.user.must_change_password = 0;

  return res.json({ success: true, message: '密码修改成功' });
});

module.exports = router;
