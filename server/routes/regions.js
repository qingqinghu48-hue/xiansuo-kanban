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

// POST /api/regions/update
router.post('/api/regions/update', requireAdmin, (req, res) => {
  try {
    const { oldName, newName } = req.body;
    const oldN = (oldName || '').trim();
    const newN = (newName || '').trim();

    if (!oldN || !newN) {
      return res.json({ success: false, message: '大区名称不能为空' });
    }
    if (oldN === newN) {
      return res.json({ success: true, message: '名称未变更' });
    }

    const oldRegion = db.prepare('SELECT id FROM regions WHERE name = ?').get(oldN);
    if (!oldRegion) {
      return res.json({ success: false, message: '原大区不存在' });
    }

    const existing = db.prepare('SELECT id FROM regions WHERE name = ?').get(newN);
    if (existing) {
      return res.json({ success: false, message: '新大区名称已存在' });
    }

    // 更新 regions 表
    db.prepare('UPDATE regions SET name = ? WHERE name = ?').run(newN, oldN);
    // 同步更新 new_leads 中包含该大区的记录（处理组合区域）
    db.prepare("UPDATE new_leads SET region = REPLACE(region, ?, ?) WHERE region LIKE ?").run(oldN, newN, `%${oldN}%`);

    res.json({ success: true, message: '大区名称已更新' });
  } catch (e) {
    console.error('[大区更新错误]', e);
    res.status(500).json({ success: false, message: '更新失败' });
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

    // 检查是否有线索归属该大区（精确匹配）
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
