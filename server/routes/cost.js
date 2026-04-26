/**
 * 成本路由
 */
const express = require('express');
const db = require('../db');
const { requireAdmin } = require('../middleware/auth');
const { formatDateTime } = require('../utils/helpers');
const { parseExcel, findCol, parseDateVal } = require('../utils/excel');
const multer = require('multer');
const upload = multer({ storage: multer.memoryStorage() });

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
    const now = formatDateTime();
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

// POST /api/cost/import — 批量导入营销成本（CSV/XLSX）
router.post('/api/cost/import', requireAdmin, upload.single('file'), (req, res) => {
  try {
    if (!req.file) {
      return res.json({ success: false, message: '请选择要导入的文件' });
    }

    const { buffer, originalname } = req.file;
    const df = parseExcel(buffer, originalname);

    if (!df || !df.length) {
      return res.json({ success: false, message: '文件为空或无法解析' });
    }

    const cols = Object.keys(df[0]).map(c => String(c).trim());
    console.log(`[成本导入] 文件=${originalname}, 行数=${df.length}, 列名=${cols.join(',')}`);

    // 智能识别列
    const dateCol = findCol(cols, ['日期', 'date', 'cost_date', '时间', '日期时间']);
    const platformCol = findCol(cols, ['平台', 'platform', '渠道', '来源平台']);
    const amountCol = findCol(cols, ['总消耗', 'amount', '消耗', '每日总消耗', '花费', '费用', '投放金额', '金额']);
    const unitCostCol = findCol(cols, ['单条成本', 'unit_cost', '单条线索成本', '单条', '线索成本', '平均成本']);

    if (!dateCol) {
      return res.json({ success: false, message: `无法识别日期列。当前列名: ${cols.join(', ')}` });
    }
    if (!platformCol) {
      return res.json({ success: false, message: `无法识别平台列。当前列名: ${cols.join(', ')}` });
    }

    const now = formatDateTime();
    let added = 0, updated = 0, skipped = 0;
    const badRows = [];

    for (let i = 0; i < df.length; i++) {
      const row = df[i];
      const rawDate = parseDateVal(row[dateCol]);
      const platform = String(row[platformCol] || '').trim();

      if (!rawDate || !platform) {
        skipped++;
        badRows.push({ row: i + 2, reason: '日期或平台为空', data: row });
        continue;
      }

      // 解析金额
      let amount = 0;
      if (amountCol) {
        const rawAmount = row[amountCol];
        if (rawAmount !== '' && rawAmount !== null && rawAmount !== undefined) {
          const parsed = parseFloat(rawAmount);
          if (!isNaN(parsed)) amount = parsed;
        }
      }

      let unit_cost = 0;
      if (unitCostCol) {
        const rawUnit = row[unitCostCol];
        if (rawUnit !== '' && rawUnit !== null && rawUnit !== undefined) {
          const parsed = parseFloat(rawUnit);
          if (!isNaN(parsed)) unit_cost = parsed;
        }
      }

      try {
        const existing = db.prepare('SELECT id, amount, unit_cost FROM cost_data WHERE cost_date = ? AND platform = ?').get(rawDate, platform);
        if (existing) {
          // 更新：如果传入值>0则覆盖，否则保留原值
          const finalAmount = amount > 0 ? amount : (existing.amount || 0);
          const finalUnitCost = unit_cost > 0 ? unit_cost : (existing.unit_cost || 0);
          db.prepare('UPDATE cost_data SET amount = ?, unit_cost = ?, created_at = ? WHERE id = ?')
            .run(finalAmount, finalUnitCost, now, existing.id);
          updated++;
        } else {
          db.prepare('INSERT INTO cost_data (cost_date, platform, amount, unit_cost, created_at) VALUES (?, ?, ?, ?, ?)')
            .run(rawDate, platform, amount, unit_cost, now);
          added++;
        }
      } catch (e) {
        skipped++;
        badRows.push({ row: i + 2, reason: e.message, data: row });
      }
    }

    let msg = `导入完成！新增 ${added} 条，更新 ${updated} 条`;
    if (skipped) msg += `，跳过/失败 ${skipped} 条`;

    return res.json({
      success: true,
      message: msg,
      added,
      updated,
      skipped,
      bad_rows: badRows.slice(0, 10),
    });
  } catch (e) {
    console.error(`[成本导入错误] ${e.message}\n${e.stack}`);
    return res.json({ success: false, message: `导入失败: ${e.message}` });
  }
});

module.exports = router;
module.exports.loadCostData = loadCostData;
