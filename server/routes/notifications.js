/**
 * 通知路由
 */
const express = require('express');
const db = require('../db');
const { requireAuth } = require('../middleware/auth');
const { loadNewLeads } = require('./leads');

const router = express.Router();

// GET /api/notifications
router.get('/api/notifications', requireAuth, (req, res) => {
  const user = req.session.user;

  if (user.role === 'admin') {
    const newLeads = loadNewLeads();
    const unread = newLeads.filter(l => l['是否已读'] === 0);
    return res.json({ unread_count: unread.length, notifications: unread });
  }

  const agentName = user.name;
  const rows = db.prepare('SELECT * FROM new_leads WHERE agent = ? AND is_read = 0 ORDER BY created_at DESC').all(agentName);

  const notifications = rows.map(row => ({
    id: row.id,
    '手机号': row.phone,
    '平台': row.platform,
    '入库时间': row.created_at ? row.created_at.slice(0, 10) : '',
  }));

  return res.json({ unread_count: notifications.length, notifications });
});

module.exports = router;
