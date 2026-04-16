import pandas as pd
import json

# 读取管理表
mgmt = pd.read_excel(r'c:\Users\Administrator\Desktop\线索\招商线索管理表.xlsx', sheet_name='线索明细')
mgmt['入库日期_dt'] = pd.to_datetime(
    mgmt['入库日期'].astype(str)
    .str.replace('年', '-').str.replace('月', '-').str.replace('日', ''),
    errors='coerce')

# 只保留3月后
mgmt = mgmt[mgmt['入库日期_dt'] >= '2026-03-01'].copy()

# 根据线索来源判断平台
def detect_platform(src):
    if pd.isna(src):
        return '未知'
    s = str(src)
    if '抖音' in s:
        return '抖音'
    if '小红书' in s:
        return '小红书'
    return '其他'

mgmt['来源平台'] = mgmt['线索来源'].apply(detect_platform)

# 只保留抖音+小红书来源的线索
mgmt = mgmt[mgmt['来源平台'].isin(['抖音', '小红书'])].copy()

# 填充空值
mgmt['日期_str'] = mgmt['入库日期_dt'].dt.strftime('%Y-%m-%d')
mgmt['月份'] = mgmt['入库日期_dt'].dt.strftime('%Y-%m')
mgmt['线索有效性'] = mgmt['线索有效性'].fillna('未知')
mgmt['所属招商'] = mgmt['所属招商'].fillna('未分配')
mgmt['所属大区'] = mgmt['所属大区'].fillna('未知')
mgmt['客户姓名_final'] = mgmt['客户姓名'].fillna('未命名')
mgmt['到访时间'] = mgmt['到访时间'].astype(str).replace('NaT', '').replace('nan', '')
mgmt['签约时间'] = mgmt['签约时间'].astype(str).replace('NaT', '').replace('nan', '')
mgmt['备注'] = mgmt['客户情况备注'].fillna('').astype(str)
mgmt['是否能加微信'] = mgmt['是否能加上微信'].fillna('').astype(str)
mgmt['手机号_clean'] = mgmt['客户电话'].astype(str).str.strip()

# 统计
total = len(mgmt)
total_valid = len(mgmt[mgmt['线索有效性'].isin(['意向客户', '一般客户'])])
total_visited = int(mgmt['到访时间'].notna().sum())
total_signed = int(mgmt['签约时间'].notna().sum())
total_dy = int((mgmt['来源平台'] == '抖音').sum())
total_xhs = int((mgmt['来源平台'] == '小红书').sum())

print(f'筛选后记录数: {total}')
print(f'  抖音: {total_dy}')
print(f'  小红书: {total_xhs}')
print(f'  有效线索: {total_valid}')
print(f'  到访: {total_visited}')
print(f'  签约: {total_signed}')

# 按维度聚合
daily = mgmt.groupby('日期_str').size().reset_index(name='count').sort_values('日期_str')
monthly = mgmt.groupby('月份').size().reset_index(name='count').sort_values('月份')
by_source = mgmt.groupby('来源平台').size().reset_index(name='count')
by_validity = mgmt.groupby('线索有效性').size().reset_index(name='count')
by_region = mgmt.groupby('所属大区').size().reset_index(name='count').sort_values('count', ascending=False)
by_recruiter = mgmt.groupby('所属招商').size().reset_index(name='count').sort_values('count', ascending=False)

# 明细表
detail_cols = ['日期_str', '月份', '来源平台', '客户姓名_final', '手机号_clean',
               '所属招商', '所属大区', '所属城市', '线索有效性',
               '是否能加微信', '备注', '到访时间', '签约时间']
detail_df = mgmt[detail_cols].copy()
detail_df.columns = ['日期', '月份', '来源平台', '姓名', '手机号',
                     '所属招商', '所属大区', '所属城市', '线索有效性',
                     '是否能加微信', '备注', '到访时间', '签约时间']

# 筛选器选项
all_months = sorted(mgmt['月份'].dropna().unique().tolist())
all_sources = sorted(mgmt['来源平台'].dropna().unique().tolist())
all_regions = sorted(mgmt['所属大区'].dropna().unique().tolist())
all_recruiters = sorted(mgmt['所属招商'].dropna().unique().tolist())
all_validity = sorted(mgmt['线索有效性'].dropna().unique().tolist())

dashboard_data = {
    'stats': {
        'total': int(total),
        'total_valid': int(total_valid),
        'total_visited': int(total_visited),
        'total_signed': int(total_signed),
        'total_dy': int(total_dy),
        'total_xhs': int(total_xhs),
    },
    'daily': daily.to_dict(orient='records'),
    'monthly': monthly.to_dict(orient='records'),
    'by_source': by_source.to_dict(orient='records'),
    'by_validity': by_validity.to_dict(orient='records'),
    'by_region': by_region.head(15).to_dict(orient='records'),
    'by_recruiter': by_recruiter.to_dict(orient='records'),
    'detail': detail_df.to_dict(orient='records'),
    'filters': {
        'months': all_months,
        'sources': all_sources,
        'regions': all_regions,
        'recruiters': all_recruiters,
        'validity': all_validity,
    }
}

with open(r'c:\Users\Administrator\Desktop\线索\dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(dashboard_data, f, ensure_ascii=False, indent=2, default=str)

print(f'\n月份范围: {all_months[0] if all_months else "N/A"} ~ {all_months[-1] if all_months else "N/A"}')
print('dashboard_data.json 已更新')
