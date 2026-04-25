/**
 * 工具函数
 */

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

/**
 * 验证手机号格式（中国大陆手机号）
 * 支持：11位手机号、座机号、以及至少7位数字的联系方式
 */
function validatePhone(phone) {
  if (!phone) return false;
  const s = String(phone).trim();
  if (s.length < 5) return false;
  // 中国大陆手机号：1开头，11位数字
  const mobileRegex = /^1[3-9]\d{9}$/;
  // 座机号：区号+号码
  const landlineRegex = /^(0\d{2,3}-?)?\d{7,8}$/;
  // 至少7位数字的通用联系方式
  const generalRegex = /^\d{7,}$/;
  return mobileRegex.test(s) || landlineRegex.test(s) || generalRegex.test(s);
}

/**
 * 清理字符串输入：去除首尾空格、XSS过滤
 */
function sanitizeString(str) {
  if (str === null || str === undefined) {
    return '';
  }
  let s = String(str).trim();
  s = htmlEscape(s);
  return s;
}

module.exports = {
  cleanVal,
  htmlEscape,
  validatePhone,
  sanitizeString,
};
