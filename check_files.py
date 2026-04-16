import openpyxl, csv, json
from pathlib import Path

base = Path(r'c:\Users\Administrator\Desktop\线索')
douyin_dir = base / '抖音客资'
xhs_dir = base / '小红书客资'

print("=== 抖音客资 xlsx 文件 ===")
for f in sorted(douyin_dir.glob('*.xlsx')):
    wb = openpyxl.load_workbook(str(f), read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    has_data = len(rows) > 1
    print(f"  {f.name}: 总行数={len(rows)}, 数据行={len(rows)-1}, 表头={rows[0] if rows else ()}")
    if has_data:
        print(f"         前2行数据: {rows[1:3]}")
        print(f"         第1行所有非空列: {[c for c in rows[0] if c]}")
        print(f"         第2行所有非空列: {[v for v in rows[1] if v]}")

print("\n=== 小红书客资 csv 文件 ===")
for f in sorted(xhs_dir.glob('*.csv')):
    with open(f, encoding='utf-8-sig') as fp:
        reader = csv.reader(fp)
        rows = list(reader)
    print(f"  {f.name}: 总行数={len(rows)}, 表头={rows[0] if rows else ()}")
    if len(rows) > 1:
        print(f"         前2行数据: {rows[1:3]}")
