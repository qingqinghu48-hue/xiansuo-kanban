"""
线索看板数据处理脚本 v5.1
口径：
  0. 客资独有线索暂存列表（用于最终输出）
  1. 抖音客资表手机号集合 → 抖音线索手机白名单
  2. 小红书客资表手机号集合 → 小红书线索手机白名单
  3. 招商线索管理表：
     - 抖音平台：手机号在客资表白名单中才收录，否则丢弃
     - 小红书平台：手机号在客资表白名单中才收录，否则丢弃
     - 其他平台：全部收录
     - 入库时间以管理表为准
  4. 客资表补充管理表已有线索的详细字段
  5. 【仅限4月12日客资】客资表独有线索（管理表无，但入库时间在2026-03-01之后的）→ 直接收录
  6. 日期过滤：入库时间 >= 2026-03-01
"""

import re, openpyxl, csv, json, pandas as pd
from pathlib import Path
from datetime import datetime

BASE    = Path('/Users/apple/Desktop/线索')
CUTOFF  = datetime(2026, 3, 1)

# ─────────────────────────────────────────────
# A. 先收集客资表手机号（抖音/小红书白名单）
# ─────────────────────────────────────────────
DY_PHONES   = set()   # 抖音客资表手机号
XHS_PHONES  = set()   # 小红书客资表手机号

def safe_str(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ''
    return str(v).strip()

# 抖音客资
for fpath in sorted((BASE / '抖音客资').glob('*.xlsx')):
    df = pd.read_excel(str(fpath), engine='openpyxl')
    for _, row in df.iterrows():
        phone = safe_str(row.get('手机号', '')).replace('.0', '')
        if phone and phone not in ('nan', '-', ''):
            DY_PHONES.add(phone)

def auto_encoding(path):
    """根据文件头字节判断编码：UTF-8-BOM / GBK"""
    raw = path.read_bytes()
    if raw[:3] == b'\xef\xbb\xbf':
        return 'utf-8-sig'
    return 'gbk'  # 默认当 GBK 处理（国内系统常见）

# 小红书客资
for subdir in sorted((BASE / '小红书客资').iterdir()):
    if not subdir.is_dir():
        continue
    for fpath in sorted(subdir.glob('*.csv')):
        enc = auto_encoding(fpath)
        with open(fpath, encoding=enc) as fp:
            rows = list(csv.reader(fp))
        if len(rows) < 2:
            continue
        headers = [h.strip() for h in rows[0]]
        for row in rows[1:]:
            if len(row) < len(headers):
                continue
            r = dict(zip(headers, row))
            phone = r.get('手机号', '').strip().replace('.0', '')
            if phone and phone not in ('-', ''):
                XHS_PHONES.add(phone)

print(f"客资表手机号白名单：抖音 {len(DY_PHONES)} 个，小红书 {len(XHS_PHONES)} 个")

# ─────────────────────────────────────────────
# B. 招商线索管理表 → 线索底座（按口径过滤）
# ─────────────────────────────────────────────
PHONE_REC = {}  # phone → record
DATA = []       # 客资独有线索（不在管理表但在客资表，特殊口径收录）

zhao_path = BASE / '招商线索管理表.xlsx'
zhao_df   = pd.read_excel(str(zhao_path), sheet_name='线索明细')

def find_col(df, *names):
    for n in names:
        for c in df.columns:
            if n in str(c):
                return c
    return None

phone_col    = find_col(zhao_df, '手机', '电话')
date_col     = find_col(zhao_df, '入库时间', '入库', '线索创建', '创建时间', '登记时间', '线索登记')
source_col   = find_col(zhao_df, '来源', '渠道', '平台')
region_col   = find_col(zhao_df, '大区', '区域')
staff_col    = find_col(zhao_df, '招商', '跟进', '负责人', '销售')
valid_col    = find_col(zhao_df, '有效性', '有效', '线索有效')
stage_col    = find_col(zhao_df, '阶段', '状态')
name_col     = find_col(zhao_df, '姓名', '客户名', '客户名称')
store_col    = find_col(zhao_df, '门店', '意向门店', '意向店')
label_col    = find_col(zhao_df, '标签')
remark_col   = find_col(zhao_df, '备注', '跟进记录')
province_col = find_col(zhao_df, '省份', '城市', '地区')
wechat_col   = find_col(zhao_df, '是否能加上微信')

print(f"招商管理表关键列映射:")
for lbl, col in [('手机', phone_col), ('日期', date_col), ('来源', source_col),
                  ('大区', region_col), ('招商员', staff_col), ('有效性', valid_col),
                  ('姓名', name_col), ('门店', store_col), ('微信', wechat_col)]:
    print(f"  {lbl} → {col}")

def parse_chinese_date(raw):
    if not raw:
        return None, ''
    s = str(raw).strip()
    m = re.match(r'(\d+)年(\d+)月(\d+)日', s)
    if m:
        dt = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        return dt, dt.strftime('%Y-%m-%d')
    try:
        dt = pd.to_datetime(raw).to_pydatetime()
        return dt, dt.strftime('%Y-%m-%d')
    except Exception:
        return None, ''

for _, row in zhao_df.iterrows():
    phone = safe_str(row.get(phone_col, '')).replace('.0', '')
    if not phone or phone in ('nan', '-', ''):
        continue

    t, t_str = parse_chinese_date(row.get(date_col, '') if date_col else '')
    if t is None or t < CUTOFF:
        continue

    src = safe_str(row.get(source_col, '')) if source_col else ''

    # 判断平台（保留原始来源作为平台名，不统一归为"其他"）
    if '抖' in src or 'Douyin' in src.lower():
        plat = '抖音'
    elif '小红书' in src or 'XHS' in src:
        plat = '小红书'
    else:
        plat = src.strip() or '其他'

    PHONE_REC[phone] = {
        '手机号': phone,
        '姓名': safe_str(row.get(name_col, '')) if name_col else '',
        '平台': plat,
        '入库时间': t_str,
        '流量类型': '',
        '线索有效性': safe_str(row.get(valid_col, '')) if valid_col else '',
        '意向门店': safe_str(row.get(store_col, '')) if store_col else '',
        '跟进员工': safe_str(row.get(staff_col, '')) if staff_col else '',
        '线索阶段': safe_str(row.get(stage_col, '')) if stage_col else '',
        '线索标签': safe_str(row.get(label_col, '')) if label_col else '',
        '线索来源': src,
        '所属大区': safe_str(row.get(region_col, '')) if region_col else '',
        '所属招商': safe_str(row.get(staff_col, '')) if staff_col else '',
        '省份': safe_str(row.get(province_col, '')) if province_col else '',
        '是否能加上微信': safe_str(row.get(wechat_col, '')) if wechat_col else '',
        '备注': safe_str(row.get(remark_col, '')) if remark_col else '',
        '来源文件': '招商线索管理表',
    }


print(f"管理表收录：{len(PHONE_REC)} 条")

print("平台分布:", {k: v for k, v in __import__('collections').Counter(r['平台'] for r in PHONE_REC.values()).items()})

# ─────────────────────────────────────────────
# C. 抖音客资表 → 补充管理表已有线索的字段
# ─────────────────────────────────────────────
dy_count = 0
for fpath in sorted((BASE / '抖音客资').glob('*.xlsx')):
    df = pd.read_excel(str(fpath), engine='openpyxl')
    for _, row in df.iterrows():
        phone = safe_str(row.get('手机号', '')).replace('.0', '')
        if not phone or phone in ('nan', '-', ''):
            continue
        r = PHONE_REC.get(phone)
        if not r:
            continue

        t_raw = row.get('线索创建时间', '')
        try:
            t = pd.to_datetime(t_raw).to_pydatetime()
            t_str = t.strftime('%Y-%m-%d')
        except Exception:
            t = None
            t_str = ''

        update = {
            '平台': '抖音',
            '入库时间': t_str,
            '姓名': r.get('姓名', '') or safe_str(row.get('姓名', '')),
            '流量类型': safe_str(row.get('流量类型', '')),
            '意向门店': safe_str(row.get('意向门店', '')) or r.get('意向门店', ''),
            '跟进员工': safe_str(row.get('跟进员工', '')) or r.get('跟进员工', ''),
            '线索阶段': safe_str(row.get('线索阶段', '')) or r.get('线索阶段', ''),
            '线索标签': safe_str(row.get('线索标签', '')) or r.get('线索标签', ''),
            '线索来源': '抖音广告',
            '省份': safe_str(row.get('所在城市', '')) or r.get('省份', ''),
            '备注': safe_str(row.get('最新跟进记录', '')) or r.get('备注', ''),
            '来源文件': fpath.name,
        }
        r.update((k, v) for k, v in update.items() if v)
        dy_count += 1

print(f"\n抖音客资补充字段：{dy_count} 条已匹配")

# ─────────────────────────────────────────────
# D2. 【仅限4月12日抖音客资】客资表独有线索（管理表无，但入库时间在2026-03-01之后的）→ 直接收录
# ─────────────────────────────────────────────
dy_new = 0
for fpath in sorted((BASE / '抖音客资').glob('*.xlsx')):
    # 只收录4月12日这一批次的文件
    if '2026-04-12' not in fpath.name:
        continue
    df = pd.read_excel(str(fpath), engine='openpyxl')
    for _, row in df.iterrows():
        phone = safe_str(row.get('手机号', '')).replace('.0', '')
        if not phone or phone in ('nan', '-', ''):
            continue
        # 只收录管理表里没有的
        if PHONE_REC.get(phone):
            continue

        t_raw = row.get('线索创建时间', '')
        try:
            t = pd.to_datetime(t_raw).to_pydatetime()
            t_str = t.strftime('%Y-%m-%d')
        except Exception:
            t = None
            t_str = ''
        if t is None or t < CUTOFF:
            continue

        new_rec = {
            '手机号': phone,
            '姓名': safe_str(row.get('姓名', '')),
            '平台': '抖音',
            '入库时间': t_str,
            '流量类型': safe_str(row.get('流量类型', '')),
            '线索有效性': '普通线索',   # 客资独有线索，暂无管理表有效性，默认为普通
            '线索阶段': safe_str(row.get('线索阶段', '')),
            '线索标签': safe_str(row.get('线索标签', '')),
            '线索来源': '抖音广告',
            '意向门店': safe_str(row.get('意向门店', '')),
            '跟进员工': safe_str(row.get('跟进员工', '')),
            '省份': safe_str(row.get('所在城市', '')),
            '备注': safe_str(row.get('最新跟进记录', '')),
            '来源文件': fpath.name,
            '是否能加上微信': '',
            '所属大区': '',
            '所属招商': '',
        }
        PHONE_REC[phone] = new_rec
        DATA.append(new_rec)
        dy_new += 1

if dy_new:
    print(f"抖音客资独有线索（管理表无）: {dy_new} 条已收录")

# ─────────────────────────────────────────────
# E. 小红书客资表 → 补充管理表已有线索的字段
# ─────────────────────────────────────────────
xhs_count = 0
for subdir in sorted((BASE / '小红书客资').iterdir()):
    if not subdir.is_dir():
        continue
    for fpath in sorted(subdir.glob('*.csv')):
        enc = auto_encoding(fpath)
        with open(fpath, encoding=enc) as fp:
            rows = list(csv.reader(fp))
        if len(rows) < 2:
            continue
        headers = [h.strip() for h in rows[0]]
        for row in rows[1:]:
            if len(row) < len(headers):
                continue
            r = dict(zip(headers, row))
            phone = r.get('手机号', '').strip().replace('.0', '')
            if not phone or phone in ('-', ''):
                continue
            existing = PHONE_REC.get(phone)
            if not existing:
                continue

            t_raw = r.get('线索生成时间', '')
            try:
                t = pd.to_datetime(t_raw).to_pydatetime()
                t_str = t.strftime('%Y-%m-%d')
            except Exception:
                t_str = ''

            detail = r.get('详情', '')
            region = ''
            if '地区:' in detail:
                try:
                    region = detail.split('地区:')[1].split(';')[0].strip()
                except Exception:
                    pass

            update = {
                '平台': '小红书',
                '入库时间': t_str,
                '姓名': existing.get('姓名', '') or r.get('用户小红书昵称', '').strip(),
                '流量类型': r.get('流量类型', '').strip() or existing.get('流量类型', ''),
                '线索标签': r.get('转化方式', '').strip() or existing.get('线索标签', ''),
                '线索来源': r.get('归属账号', '').strip() or existing.get('线索来源', ''),
                '省份': region or existing.get('省份', ''),
                '来源文件': fpath.name,
            }
            existing.update((k, v) for k, v in update.items() if v)
            xhs_count += 1

print(f"小红书客资补充字段：{xhs_count} 条已匹配")

# ─────────────────────────────────────────────
# E2. 小红书客资独有线索 - 【已禁用】仅抖音4月12日批次允许此口径
# ─────────────────────────────────────────────
pass

# ─────────────────────────────────────────────
# F. 最终输出
# ─────────────────────────────────────────────
RECORDS = list(PHONE_REC.values())
RECORDS.sort(key=lambda x: x['入库时间'], reverse=True)

by_plat = {}
for r in RECORDS:
    by_plat[r['平台']] = by_plat.get(r['平台'], 0) + 1

print(f"\n=== 最终数据统计 ===")
print(f"总线索数: {len(RECORDS)}")
for k, v in sorted(by_plat.items()):
    print(f"  {k}: {v}")

with open(BASE / 'dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(RECORDS, f, ensure_ascii=False, indent=2)

print(f"\n数据已写入 dashboard_data.json，共 {len(RECORDS)} 条")
