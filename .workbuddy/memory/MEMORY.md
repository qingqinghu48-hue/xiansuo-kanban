# 线索看板项目记忆

## 项目路径
- 工作目录：`C:\Users\Administrator\Desktop\线索`
- Skill 目录：`C:\Users\Administrator\.workbuddy\skills\leads-dashboard`

## 看板文件结构
- `线索看板.html` — 完全单文件，**Canvas 原生绘图**（竖向柱状图+SVG饼图+双Y轴折线图），零外部依赖
- ~~`data.js`~~ 已废弃（数据内嵌进 HTML）
- ~~`echarts.min.js`~~ 已废弃

## Python 环境
所有脚本必须用绝对路径：
```
C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe
```

## 数据更新流程
1. `build_dashboard.py` → 生成 `dashboard_data.json`
2. `generate_html.py` → 生成单一 `线索看板.html`（384KB，数据+ECharts图表全部内嵌）
3. 用户双击 `线索看板.html` 打开

## 数据口径
- 抖音/小红书：手机号必须在对应客资表才收录
- 客资独有线索：仅2026-04-12批次直接收录，其他批次默认丢弃
- 日期过滤：入库时间 ≥ 2026-03-01

## Skill
- `leads-dashboard`：线索看板更新 skill，备份在桌面 `leads-dashboard.zip`
