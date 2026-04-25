/**
 * 平台来源管理路由
 */
const express = require('express');
const db = require('../db');
const { requireAdmin } = require('../middleware/auth');

const router = express.Router();

// GET /api/platforms
router.get('/api/platforms', (req, res) => {
  const rows = db.prepare('SELECT * FROM platforms ORDER BY sort_order, id').all();
  res.json({ success: true, platforms: rows.map(r => r.name) });
});

// POST /api/platforms
router.post('/api/platforms', requireAdmin, (req, res) => {
  const { name } = req.body;
  const n = (name || '').trim();
  if (!n) {
    return res.json({ success: false, message: '平台名称不能为空' });
  }

  const existing = db.prepare('SELECT id FROM platforms WHERE name = ?').get(n);
  if (existing) {
    return res.json({ success: false, message: '平台名称已存在' });
  }

  const maxOrder = db.prepare('SELECT MAX(sort_order) as mo FROM platforms').get();
  const now = new Date().toISOString().replace('T', ' ').slice(0, 19);

  db.prepare('INSERT INTO platforms (name, sort_order, created_at) VALUES (?, ?, ?)')
    .run(n, (maxOrder.mo || 0) + 1, now);

  res.json({ success: true, message: '平台添加成功' });
});

// POST /api/platforms/delete
router.post('/api/platforms/delete', requireAdmin, (req, res) => {
  const { name } = req.body;
  const n = (name || '').trim();
  if (!n) {
    return res.json({ success: false, message: '平台名称不能为空' });
  }

  // 检查是否有线索数据使用了该平台
  const leadCount = db.prepare('SELECT COUNT(*) as cnt FROM new_leads WHERE platform = ?').get(n);
  if (leadCount.cnt > 0) {
    return res.json({ success: false, message: `无法删除：该平台下还有 ${leadCount.cnt} 条线索数据，请先处理或转移这些线索` });
  }

  db.prepare('DELETE FROM platforms WHERE name = ?').run(n);
  res.json({ success: true, message: '平台已删除' });
});

module.exports = router;
