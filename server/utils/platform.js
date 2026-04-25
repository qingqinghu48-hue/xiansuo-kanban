/**
 * 平台标准化工具函数
 */
const db = require('../db');

function getValidPlatforms() {
  return db.prepare('SELECT name FROM platforms ORDER BY sort_order').all().map(r => r.name);
}

function normalizePlatform(raw, validPlatforms) {
  if (!raw) return null;
  const p = String(raw).trim();
  const lower = p.toLowerCase();

  if (validPlatforms.includes(p)) return p;

  const douyinKeywords = ['抖音', 'douyin', '巨量引擎', '巨量'];
  if (douyinKeywords.some(kw => lower.includes(kw))) return '抖音';

  const xhsKeywords = ['小红书', 'xhs', 'xiaohongshu', 'redbook', '红薯'];
  if (xhsKeywords.some(kw => lower.includes(kw))) return '小红书';

  if (lower === '豆包') return '豆包';
  if (lower === '400线索' || lower === '400') return '400线索';
  if (lower === '品专') return '品专';
  if (lower === '转介绍') return '转介绍';

  return null;
}

module.exports = {
  getValidPlatforms,
  normalizePlatform,
};
