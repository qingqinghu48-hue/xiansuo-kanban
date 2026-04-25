# 线索看板 (LeadKanBan)

招商线索管理与数据分析看板系统。

## 技术栈

- **后端**: Node.js + Express + SQLite (better-sqlite3)
- **前端**: Vue 3 + Vite + Composition API
- **数据库**: SQLite
- **认证**: Express Session + Cookie，密码使用 scrypt + salt 哈希存储

## 项目结构

```
LeadKanBan/
├── server/                 # Node.js 后端
│   ├── app.js              # Express 入口
│   ├── db.js               # SQLite 数据库连接
│   ├── middleware/         # 认证中间件
│   ├── routes/             # API 路由
│   │   ├── auth.js         # 认证（登录/登出/当前用户）
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
└── dashboard_data.json     # 原始线索数据（JSON）
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

- **线索看板**：筛选、排序、分页、详情查看
- **数据可视化**：平台分布饼图、有效性饼图、消耗柱状图、成本折线图（支持数据点多时横向滚动）
- **线索管理**：录入、编辑、删除、批量删除
- **Excel 导入**：招商线索表、抖音客资、小红书客资
- **成本管理**：每日营销成本录入与统计
- **权限控制**：管理员/招商员/游客三级权限（admin 超级管理员可管理所有其他账号）
- **响应式布局**：适配桌面端、平板、手机端（断点 1200/768/640/480px）

## 部署

详见 [DEPLOY.md](./DEPLOY.md)

## 开发备忘

### 手机号唯一性
- 数据库层面：`new_leads` 表 `UNIQUE(phone)` 约束
- 录入/导入前主动查重，重复跳过或提示
- 编辑时修改手机号需检查是否与其他记录冲突

### 前端响应式陷阱
- Vue 3 `ref` 只追踪 `.value` 的重新赋值，不追踪数组内对象的属性变化
- 修改数组元素后需用 `[...arr]` 替换整个数组触发更新
- 删除/编辑操作需同时更新 `allData` 和 `filtered`

### API 返回格式一致性
- `/api/leads` 返回 `{ records: [...], total: N }`
- `/api/cost` 返回 `{ cost_data: [...] }`
- 前端需做防御性检查（`Array.isArray`），避免类型错误导致组件崩溃

### Cookie / Session
- 前端 `fetch` 必须加 `credentials: 'include'`
- 后端 CORS 需配置 `credentials: true` 且 `origin` 不能为 `*`

### 密码哈希
- 使用 Node.js 内置 `crypto.scryptSync` + 随机 salt
- 存储格式：`hex(salt):hex(hash)`
- 启动时自动迁移存量明文密码（`migratePasswords`）
- 登录/修改密码/创建用户均通过 `verifyPassword`/`hashPassword` 处理

### 响应式断点
- 1200px：KPI 3 列
- 768px：KPI 2 列、筛选栏紧凑、饼图单列
- 640px：筛选栏垂直堆叠、成本图表单列、分页换行
- 480px：KPI 单列、模态框 96% 宽度

### 事件绑定
- Vue 3 `<script setup>` 中模板 `$emit` 可能有编译兼容性问题
- 推荐在 script 中定义显式方法再绑定到模板
