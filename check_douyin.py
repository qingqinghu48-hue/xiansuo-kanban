import openpyxl
from pathlib import Path

douyin_dir = Path(r'c:\Users\Administrator\Desktop\线索\抖音客资')

for f in sorted(douyin_dir.glob('*.xlsx')):
    print(f"\n=== {f.name} ===")

    # 尝试 xlrd（旧版 xls 格式）
    try:
        import xlrd
        wb = xlrd.open_workbook(str(f))
        ws = wb.sheet_by_index(0)
        print(f"  [xlrd] 行数={ws.nrows}, 列数={ws.ncols}")
        print(f"  [xlrd] 表头: {[ws.cell_value(0, c) for c in range(ws.ncols)]}")
        if ws.nrows > 1:
            print(f"  [xlrd] 第1行: {[ws.cell_value(1, c) for c in range(ws.ncols)]}")
    except Exception as e1:
        print(f"  [xlrd] 失败: {e1}")

    # 尝试 openpyxl data_only
    try:
        wb2 = openpyxl.load_workbook(str(f), data_only=True)
        ws2 = wb2.active
        rows = list(ws2.iter_rows(values_only=True))
        wb2.close()
        print(f"  [openpyxl] 行数={len(rows)}, 最大列数={max(len(r) for r in rows) if rows else 0}")
        if rows:
            print(f"  [openpyxl] 第1行: {rows[0]}")
            if len(rows) > 1:
                print(f"  [openpyxl] 第2行: {rows[1]}")
    except Exception as e2:
        print(f"  [openpyxl] 失败: {e2}")

    # 尝试 pandas
    try:
        import pandas as pd
        df = pd.read_excel(str(f), engine='openpyxl')
        print(f"  [pandas] shape={df.shape}, columns={list(df.columns)}")
        if len(df) > 0:
            print(f"  [pandas] 前2行:\n{df.head(2).to_string()}")
    except Exception as e3:
        print(f"  [pandas] 失败: {e3}")
