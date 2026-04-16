import csv, openpyxl
from pathlib import Path

xhs_dir = Path(r'c:\Users\Administrator\Desktop\线索\小红书客资')
douyin_dir = Path(r'c:\Users\Administrator\Desktop\线索\抖音客资')

# 小红书 - 目录可能包含 csv/xlsx
print("=== 小红书客资目录 ===")
for subdir in sorted(xhs_dir.iterdir()):
    if subdir.is_dir():
        files = list(subdir.glob('*'))
        print(f"\n目录: {subdir.name}")
        for sf in files:
            print(f"  文件: {sf.name}")
            if sf.suffix == '.csv':
                with open(sf, encoding='utf-8-sig') as fp:
                    rows = list(csv.reader(fp))
                print(f"    行数={len(rows)}, 表头={rows[0] if rows else ()}")
                if len(rows) > 1:
                    print(f"    前2行: {rows[1:3]}")
            elif sf.suffix == '.xlsx':
                wb = openpyxl.load_workbook(str(sf), read_only=True, data_only=True)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
                wb.close()
                print(f"    行数={len(rows)}, 表头={rows[0] if rows else ()}")
                if len(rows) > 1:
                    print(f"    前2行: {rows[1:3]}")

# 抖音 - 目录可能包含 csv/xlsx
print("\n=== 抖音客资目录 ===")
for subdir in sorted(douyin_dir.iterdir()):
    if subdir.is_dir():
        files = list(subdir.glob('*'))
        print(f"\n目录: {subdir.name}")
        for sf in files:
            print(f"  文件: {sf.name}")
            if sf.suffix == '.csv':
                with open(sf, encoding='utf-8-sig') as fp:
                    rows = list(csv.reader(fp))
                print(f"    行数={len(rows)}, 表头={rows[0] if rows else ()}")
                if len(rows) > 1:
                    print(f"    前2行: {rows[1:3]}")
            elif sf.suffix == '.xlsx':
                wb = openpyxl.load_workbook(str(sf), read_only=True, data_only=True)
                ws = wb.active
                rows = list(ws.iter_rows(values_only=True))
                wb.close()
                print(f"    行数={len(rows)}, 表头={rows[0] if rows else ()}")
                if len(rows) > 1:
                    print(f"    前2行: {rows[1:3]}")
    elif subdir.is_file():
        print(f"  文件(根目录): {subdir.name}")
