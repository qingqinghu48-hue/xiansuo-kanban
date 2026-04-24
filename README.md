# 线索看板 (LeadKanBan)

招商线索管理与数据分析看板系统。

## 技术栈

- **后端**: Node.js + Express + SQLite (better-sqlite3)
- **前端**: Vue 3 + Vite + Composition API
- **数据库**: SQLite

## 项目结构

```
LeadKanBan/
├── server/                 # Node.js 后端
│   ├── app.js              # Express 入口
│   ├── db.js               # SQLite 数据库
│   ├── middleware/         # 认证中间件
│   ├── routes/             # API 路由
│   │   ├── auth.js         # 认证
│   │   ├── leads.js        # 线索 CRUD + 导入
│   │   ├── cost.js         # 成本管理
│   │   └── notifications.js # 通知
│   └── utils/              # 工具函数
├── client/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 页面视图
│   │   ├── components/     # 组件
│   │   ├── api.js          # API 封装
│   │   └── router.js       # 路由
│   └── vite.config.js
├── users.yaml              # 用户配置
├── leads.db                # SQLite 数据库
└── dashboard_data.json     # 原始线索数据
```

## 快速启动

### 1. 安装依赖

```bash
npm run install:all
```

### 2. 开发模式（同时启动前后端）

```bash
npm run dev
```

- 前端: http://localhost:5173
- 后端 API: http://localhost:5001

### 3. 仅启动后端

```bash
npm run dev:server
```

### 4. 仅启动前端

```bash
npm run dev:client
```

## 测试账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 招商员 | zhengjianjun | zjj001345 |
| 招商员 | liurenjie | lrj001678 |

## 功能模块

- 线索看板：筛选、排序、分页、详情查看
- 数据可视化：平台分布饼图、有效性饼图、消耗柱状图、成本折线图
- 线索管理：录入、编辑、删除、批量删除
- Excel 导入：招商线索表、抖音客资、小红书客资
- 成本管理：每日营销成本录入与统计
- 权限控制：管理员/招商员/游客三级权限
