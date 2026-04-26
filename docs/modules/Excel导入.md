# Excel 导入

## 概述
支持批量导入招商线索数据，兼容多种 Excel 格式和列名变体。

## 核心文件
- `client/src/views/AdminView.vue` — 导入界面
- `server/routes/leads.js` — 导入接口
- `server/utils/excel.js` — Excel/CSV 解析工具

## 支持的导入类型

### 1. 招商线索表
- 接口：`POST /api/leads/import`
- 智能识别列名：姓名、手机号、平台、所属大区、线索有效性、线索类型、所属招商、备注、入库日期
- 入库日期兼容"录入日期"作为备选列名

### 2. 抖音客资
- 接口：`POST /api/leads/import-douyin`
- 专门处理抖音导出的客资格式

### 3. 小红书客资
- 接口：`POST /api/leads/import`
- type = `xiaohongshu`

## 解析逻辑
- 支持 `.xlsx` / `.xls` / `.csv` 格式
- CSV 文件先用 UTF-8 解码并去除 BOM，避免中文乱码
- 逐行解析，手机号去重（同一文件内重复跳过）
- 入库前再次查重数据库（`UNIQUE(phone)`）

## 最近变更
- 2026-04-26: 修复 CSV 导入中文编码乱码（buffer → utf-8 string 再解析）
