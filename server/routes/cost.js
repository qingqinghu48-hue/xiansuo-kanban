/**
 * 成本路由
 */
const express = require('express');
const db = require('../db');
const { requireAdmin } = require('../middleware/auth');

const router = express.Router();

function loadCostData() {
  const rows = db.prepare('SELECT cost_date, platform, amount, unit_cost FROM cost_data ORDER BY cost_date ASC').all();
  return rows.map(r => ({
    date: r.cost_date,
    platform: r.platform,
    amount: r.amount,
    unit_cost: r.unit_cost || 0,
  }));
}

// GET /api/cost
router.get('/api/cost', requireAdmin, (req, res) => {
  const cost_data = loadCostData();
  res.json({ cost_data });
});

// POST /api/cost/add
router.post('/api/cost/add', requireAdmin, (req, res) => {
  const data = req.body;
  if (!data) {
    return res.json({ success: false, message: '请求数据为空' });
  }

  const cost_date = String(data.cost_date || '').trim();
  const platform = String(data.platform || '').trim();
  let amount = data.amount;
  let unit_cost = data.unit_cost;

  if (!cost_date || !platform) {
    return res.json({ success: false, message: '请填写日期和平台' });
  }

  try {
    amount = parseFloat(amount);
    if (isNaN(amount)) amount = 0;
  } catch (e) {
    return res.json({ success: false, message: '金额格式错误' });
  }

  try {
    unit_cost = parseFloat(unit_cost);
    if (isNaN(unit_cost)) unit_cost = 0;
  } catch (e) {
    unit_cost = 0;
  }

  try {
    const now = new Date().toISOString().replace('T', ' ').slice(0, 19);
    const existing = db.prepare('SELECT id FROM cost_data WHERE cost_date = ? AND platform = ?').get(cost_date, platform);

    if (existing) {
      db.prepare('UPDATE cost_data SET amount = ?, unit_cost = ?, created_at = ? WHERE id = ?').run(amount, unit_cost, now, existing.id);
    } else {
      db.prepare('INSERT INTO cost_data (cost_date, platform, amount, unit_cost, created_at) VALUES (?, ?, ?, ?, ?)')
        .run(cost_date, platform, amount, unit_cost, now);
    }

    return res.json({ success: true, message: `${platform} ${cost_date} 成本录入成功` });
  } catch (e) {
    return res.json({ success: false, message: '录入失败: ' + e.message });
  }
});

// POST /api/cost/delete
router.post('/api/cost/delete', requireAdmin, (req, res) => {
  const { cost_date, platform } = req.body;
  const cd = (cost_date || '').trim();
  const plat = (platform || '').trim();

  if (!cd || !plat) {
    return res.json({ success: false, message: '请提供日期和平台' });
  }

  const result = db.prepare('DELETE FROM cost_data WHERE cost_date = ? AND platform = ?').run(cd, plat);

  if (result.changes > 0) {
    return res.json({ success: true, message: `已删除 ${plat} ${cd} 的成本记录` });
  } else {
    return res.json({ success: false, message: '未找到该记录' });
  }
});

module.exports = router;
module.exports.loadCostData = loadCostData;
