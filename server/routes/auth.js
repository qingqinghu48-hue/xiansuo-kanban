/**
 * 认证路由
 */
const express = require('express');
const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

const router = express.Router();

const USERS_FILE = path.join(__dirname, '..', '..', 'users.yaml');

function loadUsers() {
  const content = fs.readFileSync(USERS_FILE, 'utf-8');
  return yaml.load(content);
}

// POST /api/login
router.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  const u = (username || '').trim();
  const p = (password || '').trim();

  if (!u || !p) {
    return res.json({ success: false, message: '请输入用户名和密码' });
  }

  const users = loadUsers();

  // 管理员
  if (u === users.admin.username && p === users.admin.password) {
    req.session.user = {
      username: u,
      name: users.admin.name,
      role: 'admin',
    };
    return res.json({ success: true, name: users.admin.name, role: 'admin' });
  }

  // 招商员
  for (const agent of users.agents || []) {
    if (agent.username === u && agent.password === p) {
      req.session.user = {
        username: u,
        name: agent.name,
        role: 'agent',
        regions: agent.regions || [],
      };
      return res.json({ success: true, name: agent.name, role: 'agent' });
    }
  }

  // 游客
  const guest = users.guest;
  if (guest && u === guest.username && p === guest.password) {
    req.session.user = {
      username: u,
      name: guest.name,
      role: 'guest',
    };
    return res.json({ success: true, name: guest.name, role: 'guest' });
  }

  return res.json({ success: false, message: '用户名或密码错误' });
});

// POST /api/logout
router.post('/api/logout', (req, res) => {
  req.session.destroy(() => {});
  res.json({ success: true });
});

// GET /api/current_user
router.get('/api/current_user', (req, res) => {
  const user = req.session ? req.session.user : null;
  if (user) {
    return res.json({ logged_in: true, user });
  }
  return res.json({ logged_in: false });
});

module.exports = router;
