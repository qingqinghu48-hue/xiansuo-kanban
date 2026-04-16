import pathlib, shutil, json, openpyxl

BASE = pathlib.Path(r'C:\Users\Administrator\Desktop\线索')
DATA_FILE = BASE / 'dashboard_data.json'
OUT = BASE / '线索看板_simple.html'

# 读取数据
with open(DATA_FILE, encoding='utf-8') as f:
    DATA = json.load(f)

# ECharts CDN - 用确保能访问的
ECHARTS_CDN = 'https://fastly.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js'

# 只取前3条做测试
test_data = DATA[:3]
DATA_JSON = json.dumps(test_data, ensure_ascii=False)

HTML = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>看板测试</title>
<style>
body {{font-family:sans-serif;padding:20px}}
#loading {{color:#888;padding:40px;text-align:center}}
#main {{display:none}}
.card {{background:#f5f5f5;padding:12px;margin:8px 0;border-radius:6px}}
table {{border-collapse:collapse;width:100%}}
td,th {{border:1px solid #ddd;padding:8px;font-size:13px}}
</style>
</head>
<body>

<div id="loading">数据加载中... <span id="status"></span></div>
<div id="main">
  <h2>看板测试 - {len(test_data)} 条</h2>
  <div id="cards"></div>
  <div id="charts" style="display:flex;gap:16px;margin:16px 0">
    <div id="ct" style="width:400px;height:200px;border:1px solid #ddd"></div>
  </div>
  <table id="tbl"><thead><tr><th>入库时间</th><th>平台</th><th>姓名</th><th>有效性</th></tr></thead><tbody></tbody></table>
</div>

<script src="{ECHARTS_CDN}"></script>
<script>
window.onerror = function(msg, url, line) {{
  document.getElementById('status').innerHTML = '<b style="color:red">JS错误: ' + msg + ' (行' + line + ')</b>';
  return true;
}};
document.getElementById('status').textContent = '脚本已加载';

var ALL = {DATA_JSON};
document.getElementById('status').textContent = '数据已解析: ' + ALL.length + ' 条';

(function() {{
  try {{
    var filtered = ALL.slice();
    document.getElementById('status').textContent = '筛选后: ' + filtered.length;

    // 渲染卡片
    var platCount = {{}};
    filtered.forEach(function(r) {{
      var p = r['平台'] || '其他';
      platCount[p] = (platCount[p]||0)+1;
    }});
    var cardsEl = document.getElementById('cards');
    Object.keys(platCount).forEach(function(p) {{
      cardsEl.innerHTML += '<div class="card">' + p + ': ' + platCount[p] + ' 条</div>';
    }});

    // 渲染表格
    var tbody = document.querySelector('#tbl tbody');
    filtered.forEach(function(r) {{
      var tr = document.createElement('tr');
      tr.innerHTML = '<td>'+(r['入库时间']||'')+'</td><td>'+(r['平台']||'')+'</td><td>'+(r['姓名']||'')+'</td><td>'+(r['线索有效性']||'')+'</td>';
      tbody.appendChild(tr);
    }});

    // 图表
    var chartEl = document.getElementById('ct');
    var chart = echarts.init(chartEl);
    chart.setOption({{
      title: {{text: '平台分布'}},
      tooltip: {{trigger: 'item'}},
      series: [{{
        type: 'pie',
        radius: '50%',
        data: Object.keys(platCount).map(function(k) {{ return {{name:k, value:platCount[k]}}; }})
      }}]
    }});

    document.getElementById('loading').style.display = 'none';
    document.getElementById('main').style.display = 'block';
    document.getElementById('status').textContent = '渲染完成!';
  }} catch(e) {{
    document.getElementById('status').innerHTML = '<b style="color:red">渲染出错: ' + e.message + '</b>';
    console.error(e);
  }}
}})();
</script>
</body>
</html>'''

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f'测试文件已生成: {OUT}')
print(f'文件大小: {OUT.stat().st_size} 字节')
print(f'数据条数: {len(test_data)}')
