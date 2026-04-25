/**
 * 工具函数
 */

/**
 * 获取当前时间的 YYYY-MM-DD HH:mm:ss 格式字符串
 */
function formatDateTime() {
  return new Date().toISOString().replace('T', ' ').slice(0, 19);
}

/**
 * 清理字符串值，去除换行和回车，避免破坏 JSON/JS 格式
 */
function cleanVal(val) {
  if (val === null || val === undefined) {
    return '';
  }
  let s = String(val);
  s = s.replace(/\r/g, ' ').replace(/\n/g, ' ');
  return s.trim();
}

/**
 * HTML 转义，防止 XSS
 */
function htmlEscape(val) {
  if (val === null || val === undefined) {
    return '';
  }
  let s = String(val);
  s = s.replace(/&/g, '&amp;')
       .replace(/</g, '&lt;')
       .replace(/>/g, '&gt;')
       .replace(/"/g, '&quot;')
       .replace(/'/g, '&#39;');
  return s;
}

module.exports = {
  formatDateTime,
  cleanVal,
  htmlEscape,
};
