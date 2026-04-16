import json
from pathlib import Path
from datetime import datetime

with open(r'c:\Users\Administrator\Desktop\线索\dashboard_data.json', encoding='utf-8') as f:
    data = json.load(f)

dates = [r['入库时间'] for r in data if r['入库时间']]
dates.sort()
print(f"日期范围: {dates[0]} ~ {dates[-1]}")

by_plat = {}
for r in data:
    p = r['平台']
    by_plat[p] = by_plat.get(p, 0) + 1
print("平台分布:", by_plat)

by_valid = {}
for r in data:
    v = r['线索有效性'] or '未知'
    by_valid[v] = by_valid.get(v, 0) + 1
print("有效性分布:", by_valid)
