"""
线索数据模型
"""
import json
import sqlite3

from ..config import Config
from ..utils import _clean_val


def load_data():
    """加载 dashboard_data.json（自动去重，以手机号为主键）"""
    if Config.DATA_FILE.exists():
        with open(Config.DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 去重：保留每个手机号的第一条记录
        seen = {}
        result = []
        for r in data:
            phone = str(r.get('手机号', '') or r.get('手机', '')).strip()
            if phone and phone not in seen:
                seen[phone] = True
                result.append(r)
        if len(result) < len(data):
            print(f"[去重] 原始数据 {len(data)} 条，去重后 {len(result)} 条")
        return result
    return []


def load_new_leads():
    """从 SQLite 加载新录入线索"""
    conn = sqlite3.connect(str(Config.DB_FILE))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM new_leads ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()

    leads = []
    for row in rows:
        leads.append({
            'id': row['id'],
            '手机号': _clean_val(row['phone']),
            '平台': _clean_val(row['platform']),
            '所属招商': _clean_val(row['agent']),
            '录入日期': _clean_val(row['entry_date']),
            '姓名': _clean_val(row['name']),
            '省份': _clean_val(row['city']),
            '线索有效性': _clean_val(row['validity']),
            '所属大区': _clean_val(row['region']),
            '是否能加上微信': _clean_val(row['can_wechat']),
            '备注': _clean_val(row['remark']),
            '入库时间': (_clean_val(row['created_at']) or '')[:10],
            '是否已读': row['is_read'] if 'is_read' in row.keys() else 0,
            '二次联系时间': _clean_val(row['二次联系时间']) if '二次联系时间' in row.keys() else '',
            '二次联系备注': _clean_val(row['二次联系备注']) if '二次联系备注' in row.keys() else '',
            '最近一次电联时间': _clean_val(row['最近一次电联时间']) if '最近一次电联时间' in row.keys() else '',
            '到访时间': _clean_val(row['到访时间']) if '到访时间' in row.keys() else '',
            '签约时间': _clean_val(row['签约时间']) if '签约时间' in row.keys() else '',
            '小红书账号': _clean_val(row['xhs_account']) if 'xhs_account' in row.keys() else '',
            '线索类型': _clean_val(row['lead_type']) if 'lead_type' in row.keys() else '',
            '来源文件': '手动录入'
        })
    return leads


def load_cost_data():
    """加载成本数据"""
    conn = sqlite3.connect(str(Config.DB_FILE))
    c = conn.cursor()
    c.execute('SELECT cost_date, platform, amount, unit_cost FROM cost_data ORDER BY cost_date ASC')
    rows = c.fetchall()
    conn.close()
    return [{'date': r[0], 'platform': r[1], 'amount': r[2], 'unit_cost': r[3] if r[3] else 0} for r in rows]
