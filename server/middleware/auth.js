/**
 * 认证中间件
 */
const db = require('../db');

/**
 * 校验 session 中的用户是否仍然有效（存在、未停用）
 * 如无效则销毁 session，返回 401
 */
function validateSessionUser(req, res, strict = false) {
  const sessionUser = req.session ? req.session.user : null;
  if (!sessionUser) return false;

  try {
    const user = db.prepare('SELECT id, active FROM users WHERE id = ?').get(sessionUser.id);
    if (!user) {
      // 用户已被删除
      req.session.destroy(() => {});
      return false;
    }
    if (!user.active) {
      // 用户已被停用
      req.session.destroy(() => {});
      return false;
    }
    return true;
  } catch (e) {
    console.error('[认证中间件] 校验用户失败:', e.message);
    if (strict) return false;
    // 非严格模式下（数据库异常时）允许通过，避免系统完全不可用
    return true;
  }
}

/**
 * 检查用户是否已登录
 */
function requireAuth(req, res, next) {
  if (!req.session || !req.session.user) {
    return res.status(401).json({ error: '请先登录' });
  }
  if (!validateSessionUser(req, res, true)) {
    return res.status(401).json({ error: '登录已失效，请重新登录' });
  }
  next();
}

/**
 * 检查是否为管理员
 */
function requireAdmin(req, res, next) {
  if (!req.session || !req.session.user) {
    return res.status(401).json({ success: false, message: '只有管理员可以操作' });
  }
  if (!validateSessionUser(req, res, true)) {
    return res.status(401).json({ success: false, message: '登录已失效，请重新登录' });
  }
  if (req.session.user.role !== 'admin') {
    return res.status(401).json({ success: false, message: '只有管理员可以操作' });
  }
  next();
}

module.exports = {
  requireAuth,
  requireAdmin,
  validateSessionUser,
};
