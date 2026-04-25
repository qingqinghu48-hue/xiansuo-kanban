/**
 * 成本路由
 */
const express = require('express');
const db = require('../db');
const { requireAdmin } = require('../middleware/auth');

const router = express.Router();

function loadCostData() {
  const rows = db.prepare('SELECT id, cost_date, platform, amount, unit_cost FROM cost_data ORDER BY cost_date ASC').all();
  return rows.map(r => ({
    id: r.id,
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

  // 兼容前端字段名 date / cost_date
  const cost_date = String(data.cost_date || data.date || '').trim();
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
      // 已存在则更新：如果只传了amount或unit_cost其中一个，保留另一个现有值
      const current = db.prepare('SELECT amount, unit_cost FROM cost_data WHERE id = ?').get(existing.id);
      const finalAmount = amount > 0 ? amount : (current.amount || 0);
      const finalUnitCost = unit_cost > 0 ? unit_cost : (current.unit_cost || 0);
      db.prepare('UPDATE cost_data SET amount = ?, unit_cost = ?, created_at = ? WHERE id = ?').run(finalAmount, finalUnitCost, now, existing.id);
    } else {
      db.prepare('INSERT INTO cost_data (cost_date, platform, amount, unit_cost, created_at) VALUES (?, ?, ?, ?, ?)')
        .run(cost_date, platform, amount, unit_cost, now);
    }

    return res.json({ success: true, message: `${platform} ${cost_date} 成本录入成功` });
  } catch (e) {
    return res.json({ success: false, message: '录入失败: ' + e.message });
  }
});

// POST /api/cost/update
router.post('/api/cost/update', requireAdmin, (req, res) => {
  const { id, amount, unit_cost } = req.body;
  const costId = parseInt(id, 10);
  if (isNaN(costId)) {
    return res.json({ success: false, message: '记录ID无效' });
  }

  const existing = db.prepare('SELECT id FROM cost_data WHERE id = ?').get(costId);
  if (!existing) {
    return res.json({ success: false, message: '记录不存在' });
  }

  let finalAmount, finalUnitCost;
  try {
    finalAmount = amount !== undefined ? parseFloat(amount) : undefined;
    if (isNaN(finalAmount)) finalAmount = undefined;
  } catch (e) { finalAmount = undefined; }

  try {
    finalUnitCost = unit_cost !== undefined ? parseFloat(unit_cost) : undefined;
    if (isNaN(finalUnitCost)) finalUnitCost = undefined;
  } catch (e) { finalUnitCost = undefined; }

  const current = db.prepare('SELECT amount, unit_cost FROM cost_data WHERE id = ?').get(costId);
  const setAmount = finalAmount !== undefined ? finalAmount : (current.amount || 0);
  const setUnitCost = finalUnitCost !== undefined ? finalUnitCost : (current.unit_cost || 0);

  db.prepare('UPDATE cost_data SET amount = ?, unit_cost = ? WHERE id = ?').run(setAmount, setUnitCost, costId);
  res.json({ success: true, message: '记录已更新' });
});

// POST /api/cost/delete
router.post('/api/cost/delete', requireAdmin, (req, res) => {
  const { id } = req.body;
  const costId = parseInt(id, 10);
  if (isNaN(costId)) {
    return res.json({ success: false, message: '记录ID无效' });
  }

  const result = db.prepare('DELETE FROM cost_data WHERE id = ?').run(costId);

  if (result.changes > 0) {
    return res.json({ success: true, message: '记录已删除' });
  } else {
    return res.json({ success: false, message: '未找到该记录' });
  }
});

module.exports = router;
module.exports.loadCostData = loadCostData;
