/**
 * 线索看板 Node.js 后端服务
 * 版本: 1.0.0
 */
const express = require('express');
const session = require('express-session');
const cors = require('cors');
require('dotenv').config();

const authRoutes = require('./routes/auth');
const leadsRoutes = require('./routes/leads');
const costRoutes = require('./routes/cost');
const notificationsRoutes = require('./routes/notifications');

const app = express();
const PORT = process.env.PORT || 5001;

// CORS 配置
app.use(cors({
  origin: true,
  credentials: true,
}));

// Body parser
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Session 配置
app.use(session({
  secret: 'xiansuo-kanban-secret-key-2024',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: false,
    httpOnly: true,
    maxAge: 24 * 60 * 60 * 1000, // 24小时
  },
}));

// 注册路由
app.use(authRoutes);
app.use(leadsRoutes);
app.use(costRoutes);
app.use(notificationsRoutes);

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', version: '1.0.0' });
});

// 错误处理
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ success: false, message: '服务器内部错误' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log('='.repeat(50));
  console.log('🔐 线索看板 Node.js 服务启动中...');
  console.log(`📍 访问地址: http://localhost:${PORT}`);
  console.log('='.repeat(50));
  console.log('\n测试账号：');
  console.log('  管理员: admin / admin123');
  console.log('  招商员1: zhengjianjun / zjj001345');
  console.log('  招商员2: liurenjie / lrj001678');
  console.log();
});
