# 线索看板

招商线索管理与分配平台，支持多渠道线索导入、智能去重、成本核算、权限控制等功能。

**GitHub**: https://github.com/qingqinghu48-hue/xiansuo-kanban.git

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3 + Flask + SQLite3 |
| 前端 | 原生 HTML + CSS + JavaScript |
| 认证 | Flask Session |
| 代理 | Nginx（统一入口，反向代理） |

## 功能模块

| 模块 | 功能说明 | 权限 |
|------|----------|------|
| 线索看板 | 数据可视化、筛选、排序、统计 | 全部用户 |
| 线索录入 | 单条录入、批量导入（Excel） | 管理员 |
| 抖音客资导入 | 抖音渠道线索批量导入，自动去重 | 管理员 |
| 小红书导入 | 小红书渠道线索批量导入 | 管理员 |
| 成本录入 | 抖音/小红书每日营销成本记录 | 管理员 |
| 单条成本 | 手动指定单条线索成本 | 管理员 |
| 线索管理 | 编辑、删除、批量删除、下载 Excel | 管理员/招商员 |
| 未读提醒 | 新线索实时弹窗提醒 | 招商员 |
| 权限控制 | 管理员全量，招商员仅看自己线索 | 系统 |

## 核心能力

### 智能导入识别

支持 Excel（.xlsx / .xls）批量导入，自动识别列名：

| 字段 | 可识别列名 |
|------|-----------|
| 手机号 | 手机号、手机号码、电话、联系电话、手机、phone |
| 平台 | 平台、来源、渠道、来源平台、线索来源 |
| 招商员 | 所属招商、跟进员工、负责人、招商员、员工 |
| 入库日期 | 入库日期、录入日期、日期、入库时间、录入时间 |
| 城市 | 城市、省份、地区、所在城市 |
| 线索有效性 | 线索有效性、有效性、客户类型、等级 |

### 成本自动核算

- 每日总消耗按平台（抖音/小红书）录入
- 自动计算单条线索成本 = 总消耗 / 当日线索数
- 支持手动覆盖单条成本

## 快速启动

### 前置条件

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 一键启动（开发环境）

```bash
./scripts/start.sh
```

### 手动启动

```bash
python run.py
```

服务启动后访问：http://localhost:5001

## 访问地址

| 环境 | 地址 |
|------|------|
| 生产（Nginx） | http://47.116.116.67 |
| 开发 | http://localhost:5001 |

## 默认账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 招商员 | zhengjianjun | zjj001345 |
| 招商员 | liurenjie | lrj001678 |

## 文件结构

```
LeadKanBan/
├── app/                    # 应用核心代码
│   ├── __init__.py         # 应用工厂 create_app()
│   ├── models/             # 数据模型
│   ├── routes/             # 路由定义
│   ├── services/           # 业务逻辑
│   └── utils/              # 工具函数
├── templates/              # HTML 模板
│   └── dashboard.html      # 线索看板前端页面
├── scripts/                # 脚本工具
│   ├── start.sh            # 开发环境一键启动
│   └── deploy.sh           # 生产环境部署脚本
├── logs/                   # 日志目录
├── venv/                   # Python 虚拟环境
├── run.py                  # 应用启动入口
├── requirements.txt        # Python 依赖
├── .env                    # 环境变量（不提交到 Git）
├── .gitignore              # Git 忽略配置
├── README.md               # 项目说明
├── DEPLOY.md               # 部署指南
├── leads.db                # SQLite 数据库（不提交到 Git）
├── users.yaml              # 用户配置
└── dashboard_data.json     # 原始线索数据
```

## 部署说明

详见 [DEPLOY.md](./DEPLOY.md)。

## 重要规则

- 本地改代码 → 推 GitHub → 服务器拉取（不能直接在服务器改代码）
- 更新代码用 `git checkout origin/dev -- 文件名`，**不要** `git reset --hard`（会覆盖数据库！）
- 数据库文件（leads.db）不要提交到 Git
