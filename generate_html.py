#!/usr/bin/env python3
"""generate_html.py — 线索看板 HTML 生成器（高级专业版，强兼容性）"""
import json, sys, os
from pathlib import Path
import openpyxl

BASE      = Path(__file__).parent.resolve()
HTML_OUT  = BASE / '线索看板.html'
DATA_JSON = BASE / 'dashboard_data.json'
COST_XLSX = BASE / '抖音营销线索成本统计.xlsx'

# ── 读取成本数据 ────────────────────────────────────────────────
def load_cost():
    wb = openpyxl.load_workbook(COST_XLSX)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    cost = {}
    for row in rows[1:]:
        date_raw = row[0]
        spend    = row[1] or 0
        unit     = row[2] or 0
        if date_raw:
            d = str(date_raw).replace('.', '-')
            cost[d] = {'spend': float(spend), 'unit_cost': float(unit)}
    return cost

if not DATA_JSON.exists():
    print('ERROR: dashboard_data.json not found. Run build_dashboard.py first.')
    sys.exit(1)

data = json.load(open(DATA_JSON, encoding='utf-8'))
print('Data records: ' + str(len(data)))

COST = load_cost()
cost_days = sorted(COST.keys())
print('Cost days: ' + str(len(cost_days)))

# 构建内嵌 JS 数据块
all_items = []
for rec in data:
    all_items.append(json.dumps(rec, ensure_ascii=False))
ALL_JSON = '[\n' + ',\n'.join(all_items) + '\n]'

COST_JSON = '{' + ','.join(['"' + d + '":' + json.dumps(COST[d], ensure_ascii=False) for d in cost_days]) + '}'
CDAYS_JSON = json.dumps(cost_days)

# ── HTML 模板（全面重设计版）──────────────────────────────────────
HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>招商线索看板</title>
<style>
/* ── 全局变量 ── */
:root{
  --bg:#f5f7fa;
  --surface:#ffffff;
  --surface2:#f8fafc;
  --primary:#3b82f6;
  --primary-dark:#2563eb;
  --primary-light:#eff6ff;
  --accent:#6366f1;
  --success:#10b981;
  --warning:#f59e0b;
  --danger:#ef4444;
  --text:#0f172a;
  --text-2:#475569;
  --text-3:#94a3b8;
  --border:#e2e8f0;
  --border-2:#f1f5f9;
  --shadow:0 1px 3px rgba(0,0,0,.06),0 1px 2px rgba(0,0,0,.04);
  --shadow-md:0 4px 6px -1px rgba(0,0,0,.08),0 2px 4px -1px rgba(0,0,0,.04);
  --shadow-lg:0 10px 15px -3px rgba(0,0,0,.08),0 4px 6px -2px rgba(0,0,0,.04);
  --radius:14px;
  --radius-sm:8px;
  --radius-xs:5px;
  --font:"Microsoft YaHei","PingFang SC","Helvetica Neue",Arial,sans-serif;
  --font-mono:"Consolas","JetBrains Mono",monospace;
}

/* ── 重置 ── */
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;font-family:var(--font);background:var(--bg);color:var(--text);font-size:14px;-webkit-font-smoothing:antialiased}
html{overflow-x:hidden}

/* ── 布局容器 ── */
.wrap{
  width:100%;
  min-height:100vh;
  padding:0;
}

/* ── 顶部导航 ── */
.topbar{
  background:var(--surface);
  border-bottom:1px solid var(--border);
  padding:0 28px;
  height:60px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  position:sticky;
  top:0;
  z-index:100;
  box-shadow:0 1px 0 var(--border);
}
.topbar-left{display:flex;align-items:center;gap:12px}
.brand{
  display:flex;align-items:center;gap:10px;
}
.brand-icon{
  width:36px;height:36px;
  background:linear-gradient(135deg,var(--primary),var(--accent));
  color:#fff;border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  font-weight:800;font-size:17px;letter-spacing:-1px;
}
.brand-text h1{font-size:17px;font-weight:700;color:var(--text);line-height:1.2}
.brand-text span{font-size:12px;color:var(--text-3)}
.topbar-right{font-size:12px;color:var(--text-3)}

/* ── 主内容区 ── */
.main{padding:24px 28px}

/* ── KPI 网格 ── */
.kpi-grid{
  display:grid;
  grid-template-columns:repeat(5,1fr);
  gap:16px;
  margin-bottom:20px;
}
.kpi-card{
  background:var(--surface);
  border-radius:var(--radius);
  padding:20px 22px;
  box-shadow:var(--shadow);
  border:1px solid var(--border-2);
  position:relative;
  overflow:hidden;
  transition:transform .2s,box-shadow .2s;
}
.kpi-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-md)}
.kpi-card::after{
  content:"";
  position:absolute;top:0;left:0;right:0;
  height:3px;
  border-radius:var(--radius) var(--radius) 0 0;
}
.kpi-card.blue::after{background:linear-gradient(90deg,#3b82f6,#60a5fa)}
.kpi-card.red::after{background:linear-gradient(90deg,#f43f5e,#fb7185)}
.kpi-card.amber::after{background:linear-gradient(90deg,#f59e0b,#fbbf24)}
.kpi-card.green::after{background:linear-gradient(90deg,#10b981,#34d399)}
.kpi-card.indigo::after{background:linear-gradient(90deg,#6366f1,#818cf8)}
.kpi-top{display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:14px}
.kpi-icon{
  width:38px;height:38px;border-radius:10px;
  display:flex;align-items:center;justify-content:center;
  font-size:18px;
}
.kpi-card.blue .kpi-icon{background:#dbeafe;color:var(--primary)}
.kpi-card.red .kpi-icon{background:#fee2e2;color:#f43f5e}
.kpi-card.amber .kpi-icon{background:#fef3c7;color:var(--warning)}
.kpi-card.green .kpi-icon{background:#d1fae5;color:var(--success)}
.kpi-card.indigo .kpi-icon{background:#ede9fe;color:var(--accent)}
.kpi-badge{
  background:var(--surface2);
  border:1px solid var(--border);
  border-radius:20px;
  padding:3px 8px;
  font-size:11px;
  color:var(--text-2);
}
.kpi-label{font-size:12px;color:var(--text-3);font-weight:500;margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px}
.kpi-value{font-size:30px;font-weight:800;color:var(--text);line-height:1.1;font-variant-numeric:tabular-nums}
.kpi-sub{font-size:11px;color:var(--text-3);margin-top:4px}

/* ── 筛选栏 ── */
.filter-section{
  background:var(--surface);
  border-radius:var(--radius);
  padding:16px 20px;
  margin-bottom:20px;
  box-shadow:var(--shadow);
  border:1px solid var(--border-2);
}
.filter-row{
  display:flex;gap:12px;flex-wrap:wrap;align-items:center;
}
.filter-row+ .filter-row{margin-top:10px}
.filter-label{font-size:12px;color:var(--text-2);font-weight:600;min-width:40px}
.filter-input{
  padding:8px 12px;
  border:1px solid var(--border);
  border-radius:var(--radius-sm);
  font-size:13px;
  background:var(--surface);
  color:var(--text);
  transition:border-color .15s,box-shadow .15s;
  min-width:130px;
}
.filter-input:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px rgba(59,130,246,.12)}
.filter-select{
  padding:8px 12px;
  border:1px solid var(--border);
  border-radius:var(--radius-sm);
  font-size:13px;
  background:var(--surface);
  color:var(--text);
  min-width:120px;
  cursor:pointer;
  transition:border-color .15s;
}
.filter-select:focus{outline:none;border-color:var(--primary)}
.filter-search{
  padding:8px 12px;
  border:1px solid var(--border);
  border-radius:var(--radius-sm);
  font-size:13px;
  background:var(--surface);
  color:var(--text);
  width:160px;
  transition:border-color .15s;
}
.filter-search:focus{outline:none;border-color:var(--primary);box-shadow:0 0 0 3px rgba(59,130,246,.12)}
.filter-search::placeholder{color:var(--text-3)}
.btn{padding:8px 16px;border:none;border-radius:var(--radius-sm);font-size:13px;font-weight:600;cursor:pointer;transition:all .15s}
.btn-pri{background:var(--primary);color:#fff}
.btn-pri:hover{background:var(--primary-dark)}
.btn-pri:active{transform:scale(.98)}
.btn-ghost{background:var(--surface2);color:var(--text-2);border:1px solid var(--border)}
.btn-ghost:hover{background:var(--border);color:var(--text)}

/* ── 图表区通用 ── */
.section-title{
  font-size:15px;font-weight:700;color:var(--text);
  margin-bottom:14px;
  display:flex;align-items:center;gap:8px;
}
.section-title::before{
  content:"";
  width:4px;height:18px;
  background:linear-gradient(180deg,var(--primary),var(--accent));
  border-radius:2px;
}
.section-title span{font-size:12px;font-weight:400;color:var(--text-3)}

.chart-card{
  background:var(--surface);
  border-radius:var(--radius);
  box-shadow:var(--shadow);
  border:1px solid var(--border-2);
  overflow:hidden;
}
.chart-card-head{
  padding:14px 20px;
  border-bottom:1px solid var(--border-2);
  display:flex;align-items:center;justify-content:space-between;
}
.chart-card-head h3{font-size:14px;font-weight:700;color:var(--text)}
.chart-card-head .chart-tag{
  font-size:11px;
  background:var(--primary-light);
  color:var(--primary);
  padding:3px 10px;
  border-radius:20px;
  font-weight:600;
}
.chart-card-body{padding:20px}
canvas{display:block;width:100%}

/* ── 图表布局：饼图双列 + 成本图各占一行 ── */
.charts-pies{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:16px;
  margin-bottom:16px;
}
.chart-row-full{margin-bottom:16px}

/* ── 表格卡片 ── */
.table-card{
  background:var(--surface);
  border-radius:var(--radius);
  box-shadow:var(--shadow);
  border:1px solid var(--border-2);
  overflow:hidden;
}
.table-card-head{
  padding:14px 20px;
  border-bottom:1px solid var(--border-2);
  display:flex;align-items:center;justify-content:space-between;
}
.table-card-head h2{font-size:15px;font-weight:700}
.table-badge{
  background:var(--primary-light);
  color:var(--primary);
  padding:4px 12px;
  border-radius:20px;
  font-size:12px;
  font-weight:700;
}
.table-scroll{width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;min-width:900px}
thead{background:var(--surface2)}
th{
  padding:12px 16px;
  text-align:left;
  font-size:12px;font-weight:700;
  color:var(--text-2);
  text-transform:uppercase;
  letter-spacing:.5px;
  border-bottom:1px solid var(--border);
  cursor:pointer;user-select:none;white-space:nowrap;
  transition:background .15s;
}
th:hover{background:#f1f5f9}
tbody tr{transition:background .15s}
tbody tr:nth-child(even){background:#fafbff}
tbody tr:hover{background:#f0f7ff}
td{
  padding:13px 16px;
  font-size:13px;
  border-bottom:1px solid var(--border-2);
  white-space:nowrap;
  color:var(--text);
}
.td-num{font-variant-numeric:tabular-nums;font-weight:600;color:var(--text-2)}
.td-date{color:var(--text-3);font-size:12px}

/* ── 标签 ── */
.tag{
  display:inline-block;
  padding:3px 10px;
  border-radius:var(--radius-xs);
  font-size:11px;font-weight:700;
  letter-spacing:.2px;
}
.tag-dy{background:#fee2e2;color:#dc2626}
.tag-xhs{background:#fef3c7;color:#b45309}
.tag-qt{background:#dbeafe;color:#1d4ed8}
.tag-yx{background:#d1fae5;color:#065f46}
.tag-yb{background:#dbeafe;color:#1e40af}
.tag-wlx{background:#f1f5f9;color:#475569}
.tag-pt{background:#ede9fe;color:#4338ca}
.td-btn{
  padding:4px 10px;
  border:1px solid var(--border);
  border-radius:var(--radius-xs);
  background:#fff;
  color:var(--primary);
  font-size:11px;font-weight:700;
  cursor:pointer;
  transition:all .15s;
}
.td-btn:hover{background:var(--primary);color:#fff;border-color:var(--primary)}

/* ── 分页 ── */
.pager{
  padding:12px 20px;
  background:var(--surface2);
  border-top:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}
.pager-info{font-size:13px;color:var(--text-3)}
.pager-btns{display:flex;gap:6px}
.pager-btns button{
  width:34px;height:34px;
  border:1px solid var(--border);
  border-radius:var(--radius-sm);
  background:#fff;
  cursor:pointer;
  font-size:16px;
  color:var(--text-2);
  transition:all .15s;
  display:flex;align-items:center;justify-content:center;
}
.pager-btns button:hover:not(:disabled){background:var(--primary);color:#fff;border-color:var(--primary)}
.pager-btns button:disabled{opacity:.4;cursor:not-allowed}

/* ── 弹窗 ── */
.modal{
  display:none;
  position:fixed;inset:0;
  background:rgba(15,23,42,.55);
  z-index:1000;
  backdrop-filter:blur(4px);
  align-items:center;justify-content:center;
}
.modal.show{display:flex}
.modal-box{
  background:#fff;
  border-radius:var(--radius);
  max-width:520px;width:90%;
  max-height:85vh;
  overflow:hidden;
  animation:modalIn .2s ease;
  box-shadow:var(--shadow-lg);
}
@keyframes modalIn{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:scale(1)}}
.modal-hd{
  padding:16px 20px;
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;
}
.modal-hd h3{font-size:16px;font-weight:700}
.modal-x{
  width:32px;height:32px;
  border:none;background:#f1f5f9;border-radius:var(--radius-sm);
  cursor:pointer;font-size:16px;color:var(--text-2);
  display:flex;align-items:center;justify-content:center;
  transition:background .15s;
}
.modal-x:hover{background:#e2e8f0}
.modal-bd{padding:20px;overflow-y:auto;max-height:calc(85vh - 60px)}
.detail-row{
  display:flex;padding:11px 0;
  border-bottom:1px solid var(--border-2);
}
.detail-row:last-child{border-bottom:none}
.detail-l{width:88px;flex-shrink:0;font-size:12px;color:var(--text-3);font-weight:600;padding-top:1px}
.detail-v{font-size:13px;color:var(--text)}

/* ── 加载状态 ── */
#loading{
  position:fixed;inset:0;
  background:var(--bg);
  display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  z-index:9999;
}
.spinner{
  width:44px;height:44px;
  border:3px solid var(--border);
  border-top-color:var(--primary);
  border-radius:50%;
  animation:spin .8s linear infinite;
}
.loading-text{margin-top:16px;font-size:14px;color:var(--text-3);font-weight:500}
@keyframes spin{to{transform:rotate(360deg)}}
#main{display:none}

/* ── 响应式 ── */
@media(max-width:1200px){
  .kpi-grid{grid-template-columns:repeat(3,1fr)}
}
@media(max-width:768px){
  .kpi-grid{grid-template-columns:repeat(2,1fr)}
  .charts-pies{grid-template-columns:1fr}
  .main{padding:16px}
  .topbar{padding:0 16px}
}
@media(max-width:480px){
  .kpi-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>

<div id="loading">
  <div class="spinner"></div>
  <div class="loading-text">正在加载数据...</div>
</div>

<div id="main">
  <!-- 顶部导航 -->
  <div class="topbar">
    <div class="topbar-left">
      <div class="brand">
        <div class="brand-icon">招</div>
        <div class="brand-text">
          <h1>招商线索看板</h1>
          <span>全渠道线索数据总览</span>
        </div>
      </div>
    </div>
    <div class="topbar-right" id="updateTime">-</div>
  </div>

  <!-- 主内容 -->
  <div class="main">

    <!-- 筛选栏 -->
    <div class="filter-section">
      <div class="filter-row">
        <span class="filter-label">日期</span>
        <input type="date" class="filter-input" id="ds" value="2026-03-01">
        <span style="color:var(--text-3);font-size:12px">—</span>
        <input type="date" class="filter-input" id="de" value="2026-04-30">
        <span class="filter-label" style="margin-left:8px">平台</span>
        <select class="filter-select" id="fp"><option value="">全部平台</option></select>
        <span class="filter-label">有效性</span>
        <select class="filter-select" id="fv"><option value="">全部状态</option><option>意向客户</option><option>一般客户</option><option>未联系上</option><option>普通线索</option><option>无意向客户</option><option>无效线索</option></select>
        <span class="filter-label">大区</span>
        <select class="filter-select" id="fr"><option value="">全部大区</option></select>
        <span class="filter-label">招商员</span>
        <select class="filter-select" id="fs"><option value="">全部招商</option></select>
      </div>
      <div class="filter-row">
        <span class="filter-label">搜索</span>
        <input type="text" class="filter-search" id="fk" placeholder="姓名 / 手机号">
        <div style="flex:1"></div>
        <button class="btn btn-pri" id="btnFilter">应用筛选</button>
        <button class="btn btn-ghost" id="btnReset">重置</button>
      </div>
    </div>

    <!-- KPI 卡片 -->
    <div class="kpi-grid" id="kpiGrid"></div>

    <!-- 饼图双列 -->
    <div class="charts-pies">
      <div class="chart-card">
        <div class="chart-card-head">
          <h3>平台来源分布</h3>
          <span class="chart-tag">渠道占比</span>
        </div>
        <div class="chart-card-body">
          <canvas id="cvPlat" style="height:280px"></canvas>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-card-head">
          <h3>有效性分布</h3>
          <span class="chart-tag">线索质量</span>
        </div>
        <div class="chart-card-body">
          <canvas id="cvValid" style="height:280px"></canvas>
        </div>
      </div>
    </div>

    <!-- 成本图1：每日总消耗（全宽） -->
    <div class="chart-row-full">
      <div class="section-title">每日营销总消耗 <span>（元）</span></div>
      <div class="chart-card">
        <div class="chart-card-head">
          <h3>每日总消耗走势</h3>
          <span class="chart-tag">抖音营销消耗</span>
        </div>
        <div class="chart-card-body">
          <canvas id="cvSpend" style="height:220px"></canvas>
        </div>
      </div>
    </div>

    <!-- 成本图2：单条成本（全宽） -->
    <div class="chart-row-full">
      <div class="section-title">每日单条线索成本 <span>（元/条）</span></div>
      <div class="chart-card">
        <div class="chart-card-head">
          <h3>单条成本走势</h3>
          <span class="chart-tag">线索成本</span>
        </div>
        <div class="chart-card-body">
          <canvas id="cvUnit" style="height:220px"></canvas>
        </div>
      </div>
    </div>

    <!-- 表格 -->
    <div class="table-card">
      <div class="table-card-head">
        <h2>线索明细</h2>
        <span class="table-badge" id="tableCount">0 条</span>
      </div>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th data-sort="入库日期">入库日期</th>
              <th data-sort="平台">平台</th>
              <th data-sort="姓名">姓名</th>
              <th>手机号</th>
              <th>城市</th>
              <th data-sort="有效性">有效性</th>
              <th data-sort="所属大区">大区</th>
              <th data-sort="所属招商">招商员</th>
              <th>能否加微</th>
              <th>详情</th>
            </tr>
          </thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
      <div class="pager">
        <div class="pager-info" id="pgInfo">-</div>
        <div class="pager-btns">
          <button id="prevBtn">&#8249;</button>
          <button id="nextBtn">&#8250;</button>
        </div>
      </div>
    </div>

  </div><!-- /main -->
</div><!-- /main -->

<!-- 弹窗 -->
<div class="modal" id="modal">
  <div class="modal-box">
    <div class="modal-hd">
      <h3>线索详情</h3>
      <button class="modal-x" id="modalClose">&#10005;</button>
    </div>
    <div class="modal-bd" id="modalBody"></div>
  </div>
</div>

<!-- 数据块 -->
<script>
window.__ALL__ = __ALL_DATA__;
window.__COST__ = __COST_DATA__;
window.__COST_DAYS__ = __CDAYS_DATA__;
</script>

<!-- 主逻辑 -->
<script>
(function(){
  var ALL = window.__ALL__;
  var COST = window.__COST__;
  var CDAYS = window.__COST_DAYS__;

  if (!ALL || !ALL.length) {
    var txt = document.querySelector('#loading .loading-text');
    if (txt) txt.textContent = '数据为空，请先运行 build_dashboard.py';
    return;
  }

  var utEl = document.getElementById('updateTime');
  if (utEl) utEl.textContent = '更新时间：' + new Date().toLocaleString('zh-CN');

  function esc(s) {
    s = s == null ? '' : String(s);
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  var filtered, page, PS, sortK, sortAsc;
  filtered = [];
  page = 1;
  PS = 15;
  sortK = '';
  sortAsc = true;

  // 初始化下拉
  (function() {
    var regs = {}, staffs = {}, plats = {};
    var i, r, rg, st, pl;
    for (i = 0; i < ALL.length; i++) {
      r = ALL[i];
      rg = r['所属大区'] || '';
      st = r['所属招商'] || '';
      pl = r['平台'] || '';
      if (rg) regs[rg] = true;
      if (st) staffs[st] = true;
      if (pl) plats[pl] = true;
    }
    var regKeys = Object.keys(regs).sort();
    var stfKeys = Object.keys(staffs).sort();
    var pltKeys = Object.keys(plats).sort();
    var sr = document.getElementById('fr');
    var ss = document.getElementById('fs');
    var fp = document.getElementById('fp');
    var j, o;
    for (j = 0; j < regKeys.length; j++) {
      o = document.createElement('option');
      o.value = o.text = regKeys[j];
      sr.add(o);
    }
    for (j = 0; j < stfKeys.length; j++) {
      o = document.createElement('option');
      o.value = o.text = stfKeys[j];
      ss.add(o);
    }
    for (j = 0; j < pltKeys.length; j++) {
      o = document.createElement('option');
      o.value = o.text = pltKeys[j];
      fp.add(o);
    }
  })();

  function doFilter() {
    var ds = document.getElementById('ds').value;
    var de = document.getElementById('de').value;
    var fp = document.getElementById('fp').value;
    var fv = document.getElementById('fv').value;
    var fr = document.getElementById('fr').value;
    var fs = document.getElementById('fs').value;
    var fk = (document.getElementById('fk').value || '').trim().toLowerCase();
    var result = [];
    var i, r, dt, rv, hay;
    for (i = 0; i < ALL.length; i++) {
      r = ALL[i];
      dt = String(r['入库时间'] || r['入库日期'] || '').slice(0, 10);
      if (dt && dt < ds) continue;
      if (dt && dt > de) continue;
      if (fp && r['平台'] !== fp) continue;
      if (fv && r['线索有效性'] !== fv && r['有效性'] !== fv) continue;
      if (fr && r['所属大区'] !== fr) continue;
      if (fs && r['所属招商'] !== fs) continue;
      if (fk) {
        hay = (r['姓名'] || '') + (r['手机号'] || '') + (r['手机'] || '') + (r['所属大区'] || '') + (r['所属招商'] || '');
        if (hay.toLowerCase().indexOf(fk) === -1) continue;
      }
      result.push(r);
    }
    filtered = result;
    if (sortK) sortFiltered();
    page = 1;
    renderTable();
    try { drawPlat(); } catch(e) {}
    try { drawValid(); } catch(e) {}
  }

  function sortFiltered() {
    if (!sortK) return;
    filtered.sort(function(a, b) {
      var va = a[sortK] || '';
      var vb = b[sortK] || '';
      var cmp = va < vb ? -1 : (va > vb ? 1 : 0);
      return sortAsc ? cmp : -cmp;
    });
  }

  // 绑定筛选
  document.getElementById('btnFilter').onclick = function() { doFilter(); };
  document.getElementById('btnReset').onclick = function() {
    document.getElementById('ds').value = '2026-03-01';
    document.getElementById('de').value = '2026-04-30';
    document.getElementById('fp').value = '';
    document.getElementById('fv').value = '';
    document.getElementById('fr').value = '';
    document.getElementById('fs').value = '';
    document.getElementById('fk').value = '';
    doFilter();
  };
  document.getElementById('ds').onchange = doFilter;
  document.getElementById('de').onchange = doFilter;

  // 弹窗
  document.getElementById('modalClose').onclick = function() {
    document.getElementById('modal').className = 'modal';
  };
  document.getElementById('modal').onclick = function(e) {
    if (e.target === this) this.className = 'modal';
  };

  // 平台颜色（固定调色板，支持任意平台名）
  var PLAT_PALETTE = ['#f43f5e','#f59e0b','#3b82f6','#10b981','#6366f1','#ec4899','#14b8a6','#f97316'];
  var platColorMap = {};
  function platColor(p) {
    if (platColorMap[p]) return platColorMap[p];
    var keys = Object.keys(platColorMap);
    var c = PLAT_PALETTE[keys.length % PLAT_PALETTE.length];
    platColorMap[p] = c;
    return c;
  }
  function platBg(p) {
    var c = platColor(p);
    // 根据前景色生成浅色背景（简单映射）
    var bg = {'#f43f5e':'#fee2e2','#f59e0b':'#fef3c7','#3b82f6':'#dbeafe','#10b981':'#d1fae5','#6366f1':'#ede9fe','#ec4899':'#fce7f3','#14b8a6':'#d1fae5','#f97316':'#ffedd5'};
    return bg[c] || '#f1f5f9';
  }
  function validTag(v) {
    if (v === '意向客户') return '<span class="tag tag-yx">' + esc(v) + '</span>';
    if (v === '一般客户') return '<span class="tag tag-yb">' + esc(v) + '</span>';
    if (v === '无效线索') return '<span class="tag tag-wlx">' + esc(v) + '</span>';
    if (v === '普通线索') return '<span class="tag tag-pt">' + esc(v) + '</span>';
    if (v === '无意向客户') return '<span class="tag tag-qt">' + esc(v) + '</span>';
    return '<span class="tag">' + esc(v) + '</span>';
  }
  function jmTag(jm) {
    if (jm === '是') return '<span style="color:#10b981;font-weight:700">是</span>';
    if (jm === '否') return '<span style="color:#94a3b8">否</span>';
    return '<span style="color:#94a3b8">—</span>';
  }

  function showDetail(idx) {
    var r = filtered[(page - 1) * PS + idx];
    if (!r) return;
    var html = '';
    var keys = ['姓名','手机号','手机','平台','入库时间','入库日期','线索有效性','有效性','所属大区','所属招商','备注'];
    var k, i;
    for (i = 0; i < keys.length; i++) {
      k = keys[i];
      if (r[k] != null) {
        html += '<div class="detail-row"><div class="detail-l">' + esc(k) + '</div><div class="detail-v">' + esc(r[k]) + '</div></div>';
      }
    }
    document.getElementById('modalBody').innerHTML = html;
    document.getElementById('modal').className = 'modal show';
  }

  function renderTable() {
    var tbody = document.getElementById('tbody');
    var start = (page - 1) * PS;
    var end = Math.min(start + PS, filtered.length);
    var rows = [];
    var i, r, idx, dt;
    for (i = start; i < end; i++) {
      r = filtered[i];
      idx = i - start;
      dt = String(r['入库时间'] || r['入库日期'] || '-').slice(0, 10);
      rows.push('<tr>' +
        '<td class="td-date">' + esc(dt) + '</td>' +
        '<td><span class="tag" style="background:' + platBg(r['平台']) + ';color:' + platColor(r['平台']) + '">' + esc(r['平台']) + '</span></td>' +
        '<td class="td-num">' + esc(r['姓名'] || '-') + '</td>' +
        '<td class="td-num">' + esc(r['手机号'] || r['手机'] || '-') + '</td>' +
        '<td>' + esc(r['省份'] || '-') + '</td>' +
        '<td>' + validTag(r['线索有效性'] || r['有效性'] || '') + '</td>' +
        '<td>' + esc(r['所属大区'] || '-') + '</td>' +
        '<td>' + esc(r['所属招商'] || '-') + '</td>' +
        '<td>' + jmTag(r['是否能加上微信'] || '') + '</td>' +
        '<td><button class="td-btn" onclick="parent.showDetail(' + idx + ')">查看</button></td>' +
        '</tr>');
    }
    tbody.innerHTML = rows.join('');
    document.getElementById('tableCount').textContent = filtered.length + ' 条';
    var totalPages = Math.max(1, Math.ceil(filtered.length / PS));
    document.getElementById('pgInfo').textContent =
      '第 ' + page + ' / ' + totalPages + ' 页，共 ' + filtered.length + ' 条';
    document.getElementById('prevBtn').disabled = (page <= 1);
    document.getElementById('nextBtn').disabled = (page >= totalPages);
  }

  window.showDetail = showDetail;

  document.getElementById('prevBtn').onclick = function() {
    if (page > 1) { page--; renderTable(); }
  };
  document.getElementById('nextBtn').onclick = function() {
    var totalPages = Math.max(1, Math.ceil(filtered.length / PS));
    if (page < totalPages) { page++; renderTable(); }
  };

  // 排序
  (function() {
    var ths = document.querySelectorAll('th[data-sort]');
    var i, th;
    for (i = 0; i < ths.length; i++) {
      th = ths[i];
      th.onclick = (function(t) {
        return function() {
          var k = t.getAttribute('data-sort');
          if (sortK === k) {
            sortAsc = !sortAsc;
          } else {
            sortK = k;
            sortAsc = true;
          }
          sortFiltered();
          page = 1;
          renderTable();
        };
      })(th);
    }
  })();

  // ── KPI 卡片 ────────────────────────────────────────────────
  function renderCards() {
    var total = filtered.length;
    var dy = 0, xs = 0, qt = 0;
    var totalSpend = 0, totalUnit = 0, costCnt = 0;
    var i, r, v;
    for (i = 0; i < filtered.length; i++) {
      r = filtered[i];
      if (r['平台'] === '抖音') dy++;
      else if (r['平台'] === '小红书') xs++;
      else qt++;
    }
    for (i = 0; i < CDAYS.length; i++) {
      var c = COST[CDAYS[i]];
      if (c) { totalSpend += c.spend; totalUnit += c.unit_cost; costCnt++; }
    }
    var avgUnit = costCnt > 0 ? (totalUnit / costCnt).toFixed(1) : '0';
    var fmtSpend = totalSpend >= 10000 ? (totalSpend / 10000).toFixed(1) + '万' : totalSpend.toFixed(0);
    var xsPct = total > 0 ? (xs / total * 100).toFixed(1) : '0';

    var cards = [
      { color:'blue',   icon:'&#128200;', val: total,      label:'总线索数',     sub:'筛选后合计' },
      { color:'red',    icon:'&#127775;', val: dy,          label:'抖音线索',     sub:(xs > 0 ? '+小红书 ' + xs + '条' : '') },
      { color:'amber',  icon:'&#127800;', val: xs,          label:'小红书线索',   sub:'占比' + xsPct + '%' },
      { color:'green',  icon:'&#128181;', val:'&yen;' + fmtSpend, label:'累计消耗', sub:costCnt + '天平均' },
      { color:'indigo', icon:'&#128200;', val:'&yen;' + avgUnit,   label:'单条平均成本', sub:costCnt + '天均值' },
    ];
    var j, card, html = [], row;
    for (j = 0; j < cards.length; j++) {
      card = cards[j];
      row = '<div class="kpi-card ' + card.color + '">';
      row += '<div class="kpi-top">';
      row += '<div class="kpi-icon">' + card.icon + '</div>';
      row += '<div class="kpi-badge">' + card.label + '</div>';
      row += '</div>';
      row += '<div class="kpi-label">' + card.label + '</div>';
      row += '<div class="kpi-value">' + card.val + '</div>';
      if (card.sub) row += '<div class="kpi-sub">' + card.sub + '</div>';
      row += '</div>';
      html.push(row);
    }
    document.getElementById('kpiGrid').innerHTML = html.join('');
  }

  // ── 平台饼图 ─────────────────────────────────────────────────
  function drawPlat() {
    var cv = document.getElementById('cvPlat');
    if (!cv) return;
    var d = {};
    var i, r;
    for (i = 0; i < filtered.length; i++) {
      r = filtered[i];
      var p = r['平台'] || '\u5176\u4ed6';
      d[p] = (d[p] || 0) + 1;
    }
    var keys = Object.keys(d);
    if (!keys.length) return;
    var vals = keys.map(function(k){ return d[k]; });
    var total = vals.reduce(function(a,b){ return a+b; }, 0);
    var cvColors = keys.map(function(k){ return platColor(k); });
    var W = cv.offsetWidth || 400;
    var H = parseInt(cv.style.height) || 280;
    var dpr = window.devicePixelRatio || 1;
    cv.width = W * dpr;
    cv.height = H * dpr;
    var ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    var cx = W * 0.38;
    var cy = H / 2;
    var r = Math.min(cx, cy) - 20;
    var start = -Math.PI / 2;
    var k, v, a, mid;
    for (k = 0; k < keys.length; k++) {
      v = vals[k];
      a = (v / total) * Math.PI * 2;
      ctx.fillStyle = cvColors[k];
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, r, start, start + a);
      ctx.closePath();
      ctx.fill();
      mid = start + a / 2;
      if (a / (Math.PI * 2) > 0.06) {
        var lx = cx + Math.cos(mid) * (r * 0.62);
        var ly = cy + Math.sin(mid) * (r * 0.62);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 13px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(v, lx, ly - 8);
        ctx.font = '11px sans-serif';
        ctx.fillText((v / total * 100).toFixed(1) + '%', lx, ly + 8);
      }
      start += a;
    }

    // 图例
    var lx = cx * 2 + 20;
    var legendColors = { '\u6296\u97f3': '#f43f5e', '\u5c0f\u7ea2\u4e66': '#f59e0b', '\u5176\u4ed6': '#3b82f6' };
    var lk;
    for (k = 0; k < keys.length; k++) {
      lk = keys[k];
      var ly2 = cy - (keys.length - 1) * 18 / 2 + k * 28;
      ctx.fillStyle = cvColors[k];
      ctx.fillRect(lx, ly2 - 6, 14, 14);
      ctx.fillStyle = '#334155';
      ctx.font = '13px sans-serif';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(lk + '  ' + vals[k] + '\u6761', lx + 20, ly2 + 1);
    }
  }

  // ── 有效性饼图 ───────────────────────────────────────────────
  function drawValid() {
    var cv = document.getElementById('cvValid');
    if (!cv) return;
    var d = {};
    var i, r;
    for (i = 0; i < filtered.length; i++) {
      r = filtered[i];
      var v = r['线索有效性'] || r['有效性'] || '\u672a\u77e5';
      d[v] = (d[v] || 0) + 1;
    }
    var keys = Object.keys(d);
    if (!keys.length) return;
    var vals = keys.map(function(k){ return d[k]; });
    var total = vals.reduce(function(a,b){ return a+b; }, 0);
    var colorMap = {
      '\u610f\u5411\u5ba2\u6237': '#10b981',
      '\u4e00\u822c\u5ba2\u6237': '#3b82f6',
      '\u65e0\u6548\u7ebf\u7d22': '#94a3b8',
      '\u666e\u901a\u7ebf\u7d22': '#6366f1',
      '\u65e0\u610f\u5411\u5ba2\u6237': '#f59e0b',
      '\u672a\u8054\u7cfb\u4e0a': '#f43f5e',
      '\u672a\u77e5': '#cbd5e1'
    };
    var cvColors = keys.map(function(k){ return colorMap[k] || '#94a3b8'; });
    var W = cv.offsetWidth || 400;
    var H = parseInt(cv.style.height) || 280;
    var dpr = window.devicePixelRatio || 1;
    cv.width = W * dpr;
    cv.height = H * dpr;
    var ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    var cx = W * 0.38;
    var cy = H / 2;
    var r = Math.min(cx, cy) - 20;
    var start = -Math.PI / 2;
    var k, v, a, mid;
    for (k = 0; k < keys.length; k++) {
      v = vals[k];
      a = (v / total) * Math.PI * 2;
      ctx.fillStyle = cvColors[k];
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.arc(cx, cy, r, start, start + a);
      ctx.closePath();
      ctx.fill();
      mid = start + a / 2;
      if (a / (Math.PI * 2) > 0.05) {
        var lx = cx + Math.cos(mid) * (r * 0.62);
        var ly = cy + Math.sin(mid) * (r * 0.62);
        ctx.fillStyle = '#162033';
        ctx.font = 'bold 13px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(v, lx, ly - 8);
        ctx.font = '11px sans-serif';
        ctx.fillText((v / total * 100).toFixed(1) + '%', lx, ly + 8);
      }
      start += a;
    }

    // 图例
    var lx = cx * 2 + 20;
    var lk;
    for (k = 0; k < keys.length; k++) {
      lk = keys[k];
      var ly2 = cy - (keys.length - 1) * 18 / 2 + k * 28;
      ctx.fillStyle = cvColors[k];
      ctx.fillRect(lx, ly2 - 6, 14, 14);
      ctx.fillStyle = '#334155';
      ctx.font = '13px sans-serif';
      ctx.textAlign = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(lk + '  ' + vals[k], lx + 20, ly2 + 1);
    }
  }

  // ── 总消耗柱状图（全宽单轴） ─────────────────────────────────
  function drawSpend() {
    var cv = document.getElementById('cvSpend');
    if (!cv) return;
    var days = CDAYS;
    var vals = days.map(function(d){ var c = COST[d]; return c ? c.spend : 0; });
    if (!days.length) return;

    var W = cv.offsetWidth || 800;
    var H = parseInt(cv.style.height) || 220;
    var dpr = window.devicePixelRatio || 1;
    cv.width = W * dpr;
    cv.height = H * dpr;
    var ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    var pad = { l: 55, r: 20, t: 15, b: 45 };
    var chartW = W - pad.l - pad.r;
    var chartH = H - pad.t - pad.b;
    var maxV = Math.max.apply(null, vals) || 1;
    var barW = Math.max(4, Math.min(28, (chartW / days.length) * 0.7));

    // Y轴网格
    var yTicks = 5;
    var y, yt, yLabel;
    for (yt = 0; yt <= yTicks; yt++) {
      y = pad.t + chartH - (yt / yTicks) * chartH;
      ctx.strokeStyle = '#f1f5f9';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(pad.l, y);
      ctx.lineTo(pad.l + chartW, y);
      ctx.stroke();
      ctx.fillStyle = '#94a3b8';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      yLabel = (maxV / yTicks * yt).toFixed(0);
      ctx.fillText(yLabel, pad.l - 6, y);
    }

    // 柱状
    var barGap = chartW / days.length;
    var i, v, bx, by, bh;
    var grad = ctx.createLinearGradient(0, pad.t, 0, pad.t + chartH);
    grad.addColorStop(0, '#3b82f6');
    grad.addColorStop(1, '#93c5fd');
    for (i = 0; i < vals.length; i++) {
      v = vals[i];
      bx = pad.l + i * barGap + (barGap - barW) / 2;
      bh = (v / maxV) * chartH;
      by = pad.t + chartH - bh;
      ctx.fillStyle = grad;
      ctx.fillRect(bx, by, barW, bh);
    }

    // X轴标签（每隔几个显示）
    var step = Math.ceil(days.length / 10);
    var xi;
    for (i = 0; i < days.length; i++) {
      if (i % step !== 0) continue;
      xi = pad.l + i * barGap + barGap / 2;
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText(days[i].slice(5), xi, pad.t + chartH + 6);
    }
  }

  // ── 单条成本折线图（全宽单轴） ───────────────────────────────
  function drawUnit() {
    var cv = document.getElementById('cvUnit');
    if (!cv) return;
    var days = CDAYS;
    var vals = days.map(function(d){ var c = COST[d]; return c ? c.unit_cost : 0; });
    if (!days.length) return;

    var W = cv.offsetWidth || 800;
    var H = parseInt(cv.style.height) || 220;
    var dpr = window.devicePixelRatio || 1;
    cv.width = W * dpr;
    cv.height = H * dpr;
    var ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);

    var pad = { l: 55, r: 20, t: 15, b: 45 };
    var chartW = W - pad.l - pad.r;
    var chartH = H - pad.t - pad.b;
    var maxV = Math.max.apply(null, vals) || 1;
    var minV = 0;

    // Y轴网格
    var yTicks = 5;
    var y, yt, yLabel;
    for (yt = 0; yt <= yTicks; yt++) {
      y = pad.t + chartH - (yt / yTicks) * chartH;
      ctx.strokeStyle = '#f1f5f9';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(pad.l, y);
      ctx.lineTo(pad.l + chartW, y);
      ctx.stroke();
      ctx.fillStyle = '#94a3b8';
      ctx.font = '11px sans-serif';
      ctx.textAlign = 'right';
      ctx.textBaseline = 'middle';
      yLabel = (minV + (maxV - minV) / yTicks * yt).toFixed(1);
      ctx.fillText(yLabel, pad.l - 6, y);
    }

    // 折线
    var step = chartW / (days.length - 1 || 1);
    var pts = [];
    var i, v, px, py;
    for (i = 0; i < vals.length; i++) {
      v = vals[i];
      px = pad.l + i * step;
      py = pad.t + chartH - ((v - minV) / (maxV - minV || 1)) * chartH;
      pts.push([px, py]);
    }

    // 渐变填充
    if (pts.length > 1) {
      var grad = ctx.createLinearGradient(0, pad.t, 0, pad.t + chartH);
      grad.addColorStop(0, 'rgba(245,158,11,0.25)');
      grad.addColorStop(1, 'rgba(245,158,11,0.02)');
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.moveTo(pts[0][0], pad.t + chartH);
      for (i = 0; i < pts.length; i++) {
        ctx.lineTo(pts[i][0], pts[i][1]);
      }
      ctx.lineTo(pts[pts.length - 1][0], pad.t + chartH);
      ctx.closePath();
      ctx.fill();

      // 线
      ctx.strokeStyle = '#f59e0b';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(pts[0][0], pts[0][1]);
      for (i = 1; i < pts.length; i++) ctx.lineTo(pts[i][0], pts[i][1]);
      ctx.stroke();

      // 点 + 数值
      var dotStep = Math.ceil(days.length / 15);
      for (i = 0; i < pts.length; i++) {
        if (i % dotStep !== 0 && i !== pts.length - 1) continue;
        ctx.fillStyle = '#f59e0b';
        ctx.beginPath();
        ctx.arc(pts[i][0], pts[i][1], 3.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#92400e';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.fillText(vals[i].toFixed(1), pts[i][0], pts[i][1] - 5);
      }
    }

    // X轴标签
    var xStep = Math.ceil(days.length / 10);
    for (i = 0; i < days.length; i++) {
      if (i % xStep !== 0) continue;
      var xi = pad.l + i * step;
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText(days[i].slice(5), xi, pad.t + chartH + 6);
    }
  }

  function renderAll() {
    renderCards();
    drawPlat();
    drawValid();
    drawSpend();
    drawUnit();
    renderTable();
  }

  window.onresize = function() {
    try { drawPlat(); } catch(e) {}
    try { drawValid(); } catch(e) {}
    try { drawSpend(); } catch(e) {}
    try { drawUnit(); } catch(e) {}
  };

  // 超时保护
  var timer = setTimeout(function() {
    var el = document.getElementById('loading');
    if (el) el.style.display = 'none';
    var main = document.getElementById('main');
    if (main) main.style.display = 'block';
  }, 4000);

  try {
    doFilter();
    clearTimeout(timer);
    var el = document.getElementById('loading');
    if (el) el.style.display = 'none';
    var main = document.getElementById('main');
    if (main) main.style.display = 'block';
    renderAll();
  } catch(e) {
    clearTimeout(timer);
    console.error(e);
    var txt = document.querySelector('#loading .loading-text');
    if (txt) txt.textContent = '渲染出错，请打开控制台查看：' + e.message;
  }
})();
</script>
</body>
</html>
'''

# ── 注入数据 ────────────────────────────────────────────────────
HTML = HTML.replace('__ALL_DATA__', ALL_JSON)
HTML = HTML.replace('__COST_DATA__', COST_JSON)
HTML = HTML.replace('__CDAYS_DATA__', CDAYS_JSON)

with open(HTML_OUT, 'w', encoding='utf-8') as f:
    f.write(HTML)

import os
size = os.path.getsize(HTML_OUT)
print('HTML generated: ' + str(HTML_OUT))
print('Size: ' + str(size) + ' bytes')
print('Data: ' + str(len(data)) + ' records | Cost: ' + str(len(cost_days)) + ' days')
