/**
 * 大区管理路由（仅管理员）
 */
const express = require('express');
const db = require('../db');
const { requireAdmin } = require('../middleware/auth');

const router = express.Router();

// GET /api/regions
router.get('/api/regions', requireAdmin, (req, res) => {
  try {
    const rows = db.prepare('SELECT id, name, created_at FROM regions ORDER BY name').all();
    res.json({ success: true, regions: rows.map(r => r.name) });
  } catch (e) {
    console.error('[大区查询错误]', e);
    res.status(500).json({ success: false, message: '查询失败' });
  }
});

// POST /api/regions
router.post('/api/regions', requireAdmin, (req, res) => {
  try {
    const { name } = req.body;
    const n = (name || '').trim();

    if (!n) {
      return res.json({ success: false, message: '大区名称不能为空' });
    }

    const existing = db.prepare('SELECT id FROM regions WHERE name = ?').get(n);
    if (existing) {
      return res.json({ success: false, message: '该大区已存在' });
    }

    const now = new Date().toISOString().replace('T', ' ').slice(0, 19);
    db.prepare('INSERT INTO regions (name, created_at) VALUES (?, ?)').run(n, now);

    res.json({ success: true, message: '大区添加成功' });
  } catch (e) {
    console.error('[大区添加错误]', e);
    res.status(500).json({ success: false, message: '添加失败' });
  }
});

// POST /api/regions/delete
router.post('/api/regions/delete', requireAdmin, (req, res) => {
  try {
    const { name } = req.body;
    const n = (name || '').trim();

    if (!n) {
      return res.json({ success: false, message: '大区名称不能为空' });
    }

    const region = db.prepare('SELECT id FROM regions WHERE name = ?').get(n);
    if (!region) {
      return res.json({ success: false, message: '大区不存在' });
    }

    // 检查是否有线索归属该大区
    const leads = db.prepare('SELECT COUNT(*) as cnt FROM new_leads WHERE region = ?').get(n);
    if (leads && leads.cnt > 0) {
      return res.json({ success: false, message: `该大区下有 ${leads.cnt} 条线索，无法删除` });
    }

    db.prepare('DELETE FROM regions WHERE name = ?').run(n);
    res.json({ success: true, message: '大区已删除' });
  } catch (e) {
    console.error('[大区删除错误]', e);
    res.status(500).json({ success: false, message: '删除失败' });
  }
});

module.exports = router;
