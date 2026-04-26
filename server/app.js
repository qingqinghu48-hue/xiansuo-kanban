/**
 * 线索看板 Node.js 后端服务
 * 版本: 1.0.0
 */
const express = require('express');
const session = require('express-session');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const db = require('./db');
const SqliteSessionStore = require('./utils/session-store');

const authRoutes = require('./routes/auth');
const leadsRoutes = require('./routes/leads');
const costRoutes = require('./routes/cost');
const notificationsRoutes = require('./routes/notifications');
const usersRoutes = require('./routes/users');
const platformsRoutes = require('./routes/platforms');
const regionsRoutes = require('./routes/regions');

const app = express();
const PORT = process.env.PORT || 5001;

// CORS 配置
const allowedOrigins = process.env.CORS_ORIGIN ? process.env.CORS_ORIGIN.split(',') : ['http://localhost:5173', 'http://localhost:4173'];
app.use(cors({
  origin: (origin, callback) => {
    // 生产环境允许任意来源（Nginx已做访问控制），开发环境限制localhost
    if (!origin || process.env.NODE_ENV === 'production' || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('不允许的跨域来源'));
    }
  },
  credentials: true,
}));

// Body parser
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 静态文件服务（Vue 构建产物）
app.use(express.static(path.join(__dirname, '..', 'client', 'dist')));

// Session Store（基于 SQLite，服务器重启后 session 不丢失）
const sessionStore = new SqliteSessionStore(db, { tableName: 'sessions' });
// 每小时清理一次过期 session
setInterval(() => sessionStore.gc(), 60 * 60 * 1000);

// Session 配置
const SESSION_MAX_AGE = 14 * 24 * 60 * 60 * 1000; // 14 天
app.use(session({
  store: sessionStore,
  secret: process.env.SESSION_SECRET || 'xiansuo-kanban-secret-key-2024',
  resave: false,
  saveUninitialized: false,
  rolling: true, // 每次请求刷新过期时间
  cookie: {
    secure: false, // HTTP环境下必须为false，否则浏览器不发送cookie
    httpOnly: true,
    maxAge: SESSION_MAX_AGE,
  },
}));

// 注册路由
app.use(authRoutes);
app.use(leadsRoutes);
app.use(costRoutes);
app.use(notificationsRoutes);
app.use(usersRoutes);
app.use(platformsRoutes);
app.use(regionsRoutes);

// 健康检查
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', version: '1.0.0' });
});

// 404 处理
app.use((req, res) => {
  res.status(404).json({ success: false, message: '接口不存在' });
});

// 错误处理
app.use((err, req, res, next) => {
  console.error(err.stack);

  // Multer 文件上传错误
  if (err.code === 'LIMIT_FILE_SIZE') {
    return res.status(413).json({ success: false, message: '文件大小超过限制（最大10MB）' });
  }
  if (err.message && err.message.includes('只允许上传 Excel')) {
    return res.status(400).json({ success: false, message: err.message });
  }

  res.status(500).json({ success: false, message: '服务器内部错误' });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log('='.repeat(50));
  console.log('🔐 线索看板 Node.js 服务启动中...');
  console.log(`📍 访问地址: http://localhost:${PORT}`);
  console.log('='.repeat(50));
  console.log('\n测试账号：');
  console.log('  管理员: admin / admin123');
  console.log('  招商员1: zhengjianjun / 123456');
  console.log('  招商员2: liurenjie / 123456');
  console.log();
});
