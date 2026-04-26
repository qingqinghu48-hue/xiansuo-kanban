# 线索看板 (LeadKanBan)

招商线索管理与数据分析看板系统。

## 技术栈

- **后端**: Node.js + Express + SQLite (better-sqlite3)
- **前端**: Vue 3 + Vite + Composition API + ECharts
- **数据库**: SQLite
- **认证**: Express Session + Cookie，密码使用 scrypt + salt 哈希存储

## 项目结构

```
LeadKanBan/
├── server/                 # Node.js 后端
│   ├── app.js              # Express 入口
│   ├── db.js               # SQLite 数据库连接与初始化
│   ├── middleware/         # 认证中间件
│   ├── routes/             # API 路由
│   └── utils/              # 工具函数
├── client/                 # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 页面视图
│   │   ├── components/     # 组件
│   │   ├── api.js          # API 封装
│   │   └── router.js       # 路由
│   └── vite.config.js
├── docs/modules/           # 各模块核心逻辑说明
├── scripts/                # 部署/启动脚本
└── DEPLOY.md               # 部署指南
```

## 快速启动

```bash
# 安装依赖
npm run install:all

# 开发模式（同时启动前后端）
npm run dev
# 前端: http://localhost:5173
# 后端 API: http://localhost:5001

# 仅启动后端
npm run dev:server

# 仅启动前端
npm run dev:client
```

## 功能模块

| 模块 | 简介 | 详细说明 |
|------|------|----------|
| **线索看板** | 筛选、KPI 统计、图表、线索列表 | [docs/modules/线索看板.md](./docs/modules/线索看板.md) |
| **数据可视化** | 6 个 ECharts 图表（平台分布、有效性、消耗、成本） | [docs/modules/数据可视化.md](./docs/modules/数据可视化.md) |
| **线索管理** | 新增、编辑、删除、批量删除 | [docs/modules/线索管理.md](./docs/modules/线索管理.md) |
| **Excel 导入** | 批量导入招商线索、抖音客资、小红书客资 | [docs/modules/Excel导入.md](./docs/modules/Excel导入.md) |
| **成本管理** | 每日成本录入、批量导入、自动计算单条成本 | [docs/modules/成本管理.md](./docs/modules/成本管理.md) |
| **权限控制** | 管理员/招商员/游客三级权限 | [docs/modules/权限控制.md](./docs/modules/权限控制.md) |

## 部署

详见 [DEPLOY.md](./DEPLOY.md)
