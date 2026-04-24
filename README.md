# 线索看板

招商线索管理工具，支持线索导入、批量管理、员工账号分配。

## 功能

- 线索导入：招商管理表 / 抖音客资 / 小红书客资批量导入，智能去重
- 线索明细：查看、编辑、删除、批量删除、下载 Excel
- 成本录入：抖音/小红书每日营销成本
- 权限控制：管理员全量操作，普通员工仅自己的线索
- 数据同步：自动监听 leads.db / users.yaml 变化并推送 GitHub

## 文件结构

```
server.py           # 后端 API（Flask）
线索看板.html        # 前端页面
build_dashboard.py  # 看板数据构建
sync.sh             # 数据同步脚本
DEPLOY.md           # 部署指南
requirements.txt    # Python 依赖
```

## 快速开始

```bash
pip install -r requirements.txt
python server.py    # 访问 http://localhost:5001
```

## 重要规则

- 本地改代码 → 推 GitHub → 服务器拉取（不能直接在服务器改代码）
- 更新代码用 `git checkout origin/main -- 文件名`，**不要** `git reset --hard`（会覆盖数据库！）

## GitHub

https://github.com/qingqinghu48-hue/xiansuo-kanban.git
