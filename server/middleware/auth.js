/**
 * 认证中间件
 */

/**
 * 检查用户是否已登录
 */
function requireAuth(req, res, next) {
  if (req.session && req.session.user) {
    next();
  } else {
    return res.status(401).json({ error: '请先登录' });
  }
}

/**
 * 检查是否为管理员
 */
function requireAdmin(req, res, next) {
  if (req.session && req.session.user && req.session.user.role === 'admin') {
    next();
  } else {
    return res.status(401).json({ success: false, message: '只有管理员可以操作' });
  }
}

module.exports = {
  requireAuth,
  requireAdmin,
};
