import pathlib, json

BASE = pathlib.Path(r'C:\Users\Administrator\Desktop\线索')
DATA_FILE = BASE / 'dashboard_data.json'
ECHARTS_FILE = BASE / 'echarts.min.js'
OUT = BASE / '线索看板_diag.html'

with open(DATA_FILE, encoding='utf-8') as f:
    DATA = json.load(f)
with open(ECHARTS_FILE, encoding='utf-8') as f:
    ECHARTS_CODE = f.read()

DATA_JSON = json.dumps(DATA, ensure_ascii=False)

# 简化版看板（不依赖CDN，完全自包含）
HTML = '''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>线索看板</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f0f2f5;color:#333;font-size:14px}
#loading{text-align:center;padding:80px 0;font-size:16px;color:#888}
#main{display:none}
#error-msg{background:#fff0f0;border:1px solid #fdd;border-radius:8px;padding:16px;margin:16px;color:#c00;display:none}
.hdr{background:#2563eb;color:#fff;padding:16px 24px;font-size:18px;font-weight:600}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px;padding:16px 24px}
.card{background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.08)}
.card .lbl{font-size:12px;color:#888;margin-bottom:4px}
.card .val{font-size:26px;font-weight:700}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:8px 12px;border-bottom:1px solid #eee;text-align:left}
th{background:#fafafa;font-weight:500;cursor:pointer}
</style>
</head>
<body>

<div id="loading">数据加载中... <span id="status"></span></div>
<div id="error-msg"></div>
<div id="main">
  <div class="hdr">线索看板</div>
  <div class="cards" id="cards"></div>
  <div id="charts" style="display:grid;grid-template-columns:1fr 1fr;gap:12px;padding:0 24px 16px">
    <div style="background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.08)"><h3 style="font-size:13px;color:#888;margin-bottom:10px">每日入库</h3><div id="ct1" style="height:200px"></div></div>
    <div style="background:#fff;border-radius:8px;padding:16px;box-shadow:0 1px 3px rgba(0,0,0,.08)"><h3 style="font-size:13px;color:#888;margin-bottom:10px">平台来源</h3><div id="ct2" style="height:200px"></div></div>
  </div>
  <div style="background:#fff;margin:0 24px 24px;border-radius:8px;overflow:hidden">
    <table>
      <thead><tr><th>入库时间</th><th>平台</th><th>姓名</th><th>手机号</th><th>有效性</th><th>大区</th><th>招商员</th></tr></thead>
      <tbody id="tbody"></tbody>
    </table>
  </div>
</div>

<script>
// 全局错误捕获
window.onerror = function(msg, src, line, col, err) {
  var el = document.getElementById('error-msg');
  if (el) {
    el.style.display = 'block';
    el.innerHTML = '<b>JS错误:</b> ' + msg + '<br><small>行号: ' + line + '</small>';
  }
  console.error('JS Error:', msg, 'line:', line, 'col:', col);
  document.getElementById('loading').style.display = 'none';
  return true;
};
document.getElementById('status').textContent = '(window.onerror已设置)';
</script>
'''

# 插入echarts
HTML += '<script>' + ECHARTS_CODE + '</script>\n'

# 插入数据
HTML += '<script>\n'
HTML += 'document.getElementById("status").textContent = "ECharts版本: " + (typeof echarts !== "undefined" ? echarts.version : "未定义");\n'
HTML += 'var ALL = ' + DATA_JSON + ';\n'
HTML += 'document.getElementById("status").textContent += " | 数据: " + ALL.length + " 条";\n'
HTML += 'console.log("echarts:", typeof echarts);\n'
HTML += 'console.log("ALL:", ALL.length, "records");\n'
HTML += 'try {\n'

# 初始化逻辑
HTML += '''
  var filtered = ALL.slice();
  document.getElementById("status").textContent += " | 筛选:" + filtered.length;

  // 卡片
  var platCount = {};
  filtered.forEach(function(r){ var p=r["平台"]||"其他"; platCount[p]=(platCount[p]||0)+1; });
  var validCount = 0;
  filtered.forEach(function(r){ if(r["线索有效性"]==="意向客户"||r["线索有效性"]==="一般客户") validCount++; });
  var items = [
    ["总线索", filtered.length],
    ["抖音", platCount["抖音"]||0],
    ["小红书", platCount["小红书"]||0],
    ["其他", platCount["其他"]||0],
    ["有效线索", validCount],
  ];
  var cardsEl = document.getElementById("cards");
  items.forEach(function(it){
    var d = document.createElement("div");
    d.className = "card";
    d.innerHTML = "<div class=lbl>"+it[0]+"</div><div class=val>"+it[1]+"</div>";
    cardsEl.appendChild(d);
  });

  // 图表
  var dc = {};
  filtered.forEach(function(r){ var t=r["入库时间"]; if(t) dc[t]=(dc[t]||0)+1; });
  var days = Object.keys(dc).sort();
  if (typeof echarts !== "undefined") {
    var c1 = echarts.init(document.getElementById("ct1"));
    c1.setOption({tooltip:{trigger:"axis"},xAxis:{type:"category",data:days},yAxis:{type:"value"},series:[{type:"bar",data:days.map(function(d){return dc[d];})}]});
    var pdata = Object.keys(platCount).map(function(k){return{name:k,value:platCount[k]};});
    var c2 = echarts.init(document.getElementById("ct2"));
    c2.setOption({tooltip:{trigger:"item",formatter:"{b}:{c}"},series:[{type:"pie",radius:["35%","65%"],data:pdata}]});
    document.getElementById("status").textContent += " | 图表渲染OK";
  } else {
    document.getElementById("ct1").innerHTML = "<p style=color:#c00>echarts未定义! 无法渲染图表</p>";
    document.getElementById("ct2").innerHTML = "<p style=color:#c00>echarts未定义!</p>";
    document.getElementById("status").textContent += " | 图表跳过(echarts未定义)";
  }

  // 表格
  var start = 0;
  var page = filtered.slice(start, start + 20);
  var tbody = document.getElementById("tbody");
  page.forEach(function(r){
    var tr = document.createElement("tr");
    tr.innerHTML = "<td>"+(r["入库时间"]||"")+"</td><td>"+(r["平台"]||"")+"</td><td>"+(r["姓名"]||"")+"</td><td>"+(r["手机号"]||"")+"</td><td>"+(r["线索有效性"]||"")+"</td><td>"+(r["所属大区"]||"")+"</td><td>"+(r["所属招商"]||"")+"</td>";
    tbody.appendChild(tr);
  });
'''

HTML += '''  document.getElementById("loading").style.display = "none";
  document.getElementById("main").style.display = "block";
  document.getElementById("status").textContent += " | 完成!";
} catch(e) {
  var el = document.getElementById("error-msg");
  el.style.display = "block";
  el.innerHTML = "<b>渲染出错:</b> " + e.message + "<br><b>Stack:</b> <pre>" + (e.stack||"") + "</pre>";
  console.error(e);
}
</script>
'''

HTML += '</body></html>'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f'诊断文件已生成: {OUT}')
print(f'文件大小: {OUT.stat().st_size} 字节')
print(f'数据条数: {len(DATA)}')
