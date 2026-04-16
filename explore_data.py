import pandas as pd
import glob, json, chardet

# 抖音客资
dy_files = glob.glob(r"c:\Users\Administrator\Desktop\线索\抖音客资\*.xlsx")
print("=== 抖音客资文件 ===")
for f in dy_files:
    df = pd.read_excel(f, nrows=3)
    print(f"\n文件: {f}")
    print("列名:", list(df.columns))
    print(df.head(2).to_string())

# 小红书客资
xhs_files = glob.glob(r"c:\Users\Administrator\Desktop\线索\小红书客资\**\*.csv", recursive=True)
print("\n=== 小红书客资文件 ===")
for f in xhs_files:
    with open(f, 'rb') as fp:
        enc = chardet.detect(fp.read(10000))['encoding']
    print(f"\n文件: {f}, encoding: {enc}")
    df = pd.read_csv(f, encoding=enc, nrows=3)
    print("列名:", list(df.columns))
    print(df.head(2).to_string())

# 招商线索管理表
print("\n=== 招商线索管理表 ===")
xls = pd.read_excel(r"c:\Users\Administrator\Desktop\线索\招商线索管理表.xlsx", sheet_name=None)
for sheet_name, df in xls.items():
    print(f"\nSheet: {sheet_name}")
    print("列名:", list(df.columns))
    print(f"行数: {len(df)}")
    print(df.head(3).to_string())
