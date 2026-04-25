/**
 * Excel 导入工具函数
 */
const xlsx = require('xlsx');

function parseExcel(buffer, filename) {
  const workbook = xlsx.read(buffer, { type: 'buffer', cellDates: true });

  let worksheet = null;

  for (const sn of workbook.SheetNames) {
    const ws = workbook.Sheets[sn];
    const range = xlsx.utils.decode_range(ws['!ref'] || 'A1');
    const rowCount = range.e.r - range.s.r;
    if (rowCount > 0) {
      worksheet = ws;
      break;
    }
  }

  if (!worksheet) {
    throw new Error('Excel 文件为空（0行数据）');
  }

  return xlsx.utils.sheet_to_json(worksheet, { defval: '' });
}

function findCol(cols, keywords) {
  for (const kw of keywords) {
    const kwLower = kw.toLowerCase();
    for (const col of cols) {
      if (col.toLowerCase().includes(kwLower)) {
        return col;
      }
    }
  }
  return null;
}

function getVal(row, col) {
  if (!col) return '';
  const v = row[col];
  if (v === null || v === undefined) return '';
  const s = String(v).trim();
  return s.toLowerCase() === 'nan' ? '' : s;
}

function parseDateVal(v) {
  if (v === null || v === undefined || v === '') return '';
  if (v instanceof Date) {
    const y = v.getFullYear();
    const m = String(v.getMonth() + 1).padStart(2, '0');
    const d = String(v.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  }
  // Excel 日期序列号（如 46085.5539）
  if (typeof v === 'number' && v > 30000 && v < 60000) {
    const parsed = xlsx.SSF.parse_date_code(v);
    if (parsed && parsed.y) {
      const m = String(parsed.m).padStart(2, '0');
      const d = String(parsed.d).padStart(2, '0');
      return `${parsed.y}-${m}-${d}`;
    }
  }
  const s = String(v).trim();
  const isoMatch = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (isoMatch) return `${isoMatch[1]}-${isoMatch[2]}-${isoMatch[3]}`;
  const cnMatch = s.match(/(\d{4})年(\d{1,2})月(\d{1,2})日/);
  if (cnMatch) {
    return `${cnMatch[1]}-${String(cnMatch[2]).padStart(2, '0')}-${String(cnMatch[3]).padStart(2, '0')}`;
  }
  const d = new Date(v);
  if (!isNaN(d.getTime())) {
    const y = d.getFullYear();
    if (y >= 2000 && y <= 2100) {
      const m = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${y}-${m}-${day}`;
    }
  }
  return '';
}

function parseDate(row, col) {
  if (!col) return '';
  return parseDateVal(row[col]);
}

module.exports = {
  parseExcel,
  findCol,
  getVal,
  parseDateVal,
  parseDate,
};
