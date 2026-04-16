import csv
from pathlib import Path

xhs_dir = Path(r'c:\Users\Administrator\Desktop\线索\小红书客资')
print("小红书目录文件列表:", list(xhs_dir.iterdir()))

for f in sorted(xhs_dir.glob('*')):
    if f.is_file():
        print(f"\n--- {f.name} ---")
        with open(f, encoding='utf-8-sig') as fp:
            reader = csv.reader(fp)
            rows = list(reader)
        print(f"总行数={len(rows)}, 表头={rows[0] if rows else ()}")
        if len(rows) > 1:
            print(f"第2行: {rows[1]}")
            # 找出时间相关列
            for i, h in enumerate(rows[0]):
                if h and ('时间' in str(h) or '日期' in str(h) or 'create' in str(h).lower() or 'entry' in str(h).lower()):
                    print(f"  时间相关列[{i}] '{h}' = {rows[1][i] if i < len(rows[1]) else 'N/A'}")
