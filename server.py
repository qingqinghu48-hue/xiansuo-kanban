"""
线索看板后端服务 v2
版本: 4.22.003
- 用户认证和数据 API
- 线索分配功能
"""

from flask import Flask, request, jsonify, session, render_template_string
import yaml, json, os, sqlite3, re
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'xiansuo-kanban-secret-key-2024'

BASE_DIR = Path(__file__).parent
USERS_FILE = BASE_DIR / 'users.yaml'
DATA_FILE = BASE_DIR / 'dashboard_data.json'
DB_FILE = BASE_DIR / 'leads.db'

# ─────────────────────────────────────────────
# 数据库初始化
# ─────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS new_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            platform TEXT NOT NULL,
            agent TEXT NOT NULL,
            entry_date TEXT DEFAULT '',
            name TEXT DEFAULT '',
            city TEXT DEFAULT '',
            validity TEXT DEFAULT '',
            region TEXT DEFAULT '',
            can_wechat TEXT DEFAULT '',
            remark TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            UNIQUE(phone)
        )
    ''')
    # 线索成本表
    c.execute('''
        CREATE TABLE IF NOT EXISTS cost_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cost_date TEXT NOT NULL,
            platform TEXT NOT NULL,
            amount REAL NOT NULL,
            unit_cost REAL DEFAULT 0,
            created_at TEXT NOT NULL,
            UNIQUE(cost_date, platform)
        )
    ''')
    # 兼容旧表：若缺少 unit_cost 列则添加
    try:
        c.execute('SELECT unit_cost FROM cost_data LIMIT 1')
    except sqlite3.OperationalError:
        c.execute('ALTER TABLE cost_data ADD COLUMN unit_cost REAL DEFAULT 0')
    conn.commit()
    conn.close()

init_db()

# 加载用户配置
def load_users():
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

# 加载原始线索数据
def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# 加载新录入线索
def load_new_leads():
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('SELECT * FROM new_leads ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    
    leads = []
    for row in rows:
        def clean(val):
            if val is None:
                return ''
            s = str(val)
            # 去除换行和回车，避免破坏 JSON/JS 格式
            s = s.replace('\r', ' ').replace('\n', ' ')
            return s.strip()

        leads.append({
            'id': row[0],
            '手机号': clean(row[1]),
            '平台': clean(row[2]),
            '所属招商': clean(row[3]),
            '录入日期': clean(row[12]),
            '姓名': clean(row[4]),
            '省份': clean(row[5]),
            '线索有效性': clean(row[6]),
            '所属大区': clean(row[7]),
            '是否能加上微信': clean(row[8]),
            '备注': clean(row[9]),
            '入库时间': clean(row[12]) or (clean(row[10])[:10] if len(row) > 10 else ''),
            '是否已读': row[11] if len(row) > 11 else 0,
            '二次联系时间': clean(row[13]),
            '二次联系备注': clean(row[14]),
            '最近一次电联时间': clean(row[15]),
            '到访时间': clean(row[16]),
            '签约时间': clean(row[17]),
            '来源文件': '手动录入'
        })
    return leads

# 加载成本数据
def load_cost_data():
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('SELECT cost_date, platform, amount, unit_cost FROM cost_data ORDER BY cost_date ASC')
    rows = c.fetchall()
    conn.close()
    return [{'date': r[0], 'platform': r[1], 'amount': r[2], 'unit_cost': r[3] if r[3] else 0} for r in rows]

# ─────────────────────────────────────────────
# 登录接口
# ─────────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not password:
        return jsonify({'success': False, 'message': '请输入用户名和密码'})
    
    users = load_users()
    
    if username == users['admin']['username'] and password == users['admin']['password']:
        session['user'] = {
            'username': username,
            'name': users['admin']['name'],
            'role': 'admin'
        }
        return jsonify({'success': True, 'name': users['admin']['name'], 'role': 'admin'})
    
    for agent in users.get('agents', []):
        if agent['username'] == username and agent['password'] == password:
            session['user'] = {
                'username': username,
                'name': agent['name'],
                'role': 'agent',
                'regions': agent.get('regions', [])
            }
            return jsonify({'success': True, 'name': agent['name'], 'role': 'agent'})
    
    return jsonify({'success': False, 'message': '用户名或密码错误'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/current_user', methods=['GET'])
def current_user():
    user = session.get('user')
    if user:
        return jsonify({'logged_in': True, 'user': user})
    return jsonify({'logged_in': False})

# ─────────────────────────────────────────────
# 线索数据 API（合并原始数据 + 新录入线索）
# ─────────────────────────────────────────────
@app.route('/api/leads', methods=['GET'])
def get_leads():
    user = session.get('user')
    if not user:
        return jsonify({'error': '请先登录'}), 401
    
    records = load_data()
    new_leads = load_new_leads()
    
    # 管理员看全部
    if user['role'] == 'admin':
        all_records = records + new_leads
        return jsonify({'records': all_records, 'total': len(all_records), 'new_leads_count': len(new_leads)})
    
    # 招商员只看自己分配的
    agent_name = user['name']
    filtered = [r for r in records if r.get('所属招商', '') == agent_name 
                or r.get('跟进员工', '') == agent_name]
    
    # 加上新录入的线索
    agent_new_leads = [r for r in new_leads if r.get('所属招商', '') == agent_name]
    all_filtered = filtered + agent_new_leads
    
    # 获取未读新线索数
    unread = len([r for r in agent_new_leads if r.get('是否已读', 1) == 0])
    
    return jsonify({
        'records': all_filtered, 
        'total': len(all_filtered), 
        'role': 'agent',
        'new_leads_count': len(agent_new_leads),
        'unread_count': unread
    })

# ─────────────────────────────────────────────
# 新线索录入 API（管理员）
# ─────────────────────────────────────────────
@app.route('/api/leads/add', methods=['POST'])
def add_lead():
    user = session.get('user')
    if not user or user['role'] != 'admin':
        return jsonify({'success': False, 'message': '只有管理员可以录入线索'}), 401
    
    data = request.json
    phone = data.get('phone', '').strip()
    platform = data.get('platform', '').strip()
    agent = data.get('agent', '').strip()
    entry_date = data.get('entry_date', '').strip() or datetime.now().strftime('%Y-%m-%d')
    
    if not phone or not platform or not agent:
        return jsonify({'success': False, 'message': '请填写完整信息'})
    
    # 检查是否已存在
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('SELECT id FROM new_leads WHERE phone = ?', (phone,))
    if c.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': '该手机号已录入'})
    
    # 插入新线索
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''
        INSERT INTO new_leads (phone, platform, agent, entry_date, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (phone, platform, agent, entry_date, now))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '线索录入成功'})

# ─────────────────────────────────────────────
# 线索成本录入 API（管理员）
# ─────────────────────────────────────────────
@app.route('/api/cost/add', methods=['POST'])
def add_cost():
    user = session.get('user')
    if not user or user['role'] != 'admin':
        return jsonify({'success': False, 'message': '只有管理员可以录入成本'}), 401
    
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'})
    except Exception as e:
        return jsonify({'success': False, 'message': '请求解析失败: ' + str(e)})
    
    cost_date = str(data.get('cost_date', '')).strip()
    platform = str(data.get('platform', '')).strip()
    amount = data.get('amount', 0)
    unit_cost = data.get('unit_cost', 0)
    
    if not cost_date or not platform:
        return jsonify({'success': False, 'message': '请填写日期和平台'})
    
    try:
        amount = float(amount)
    except:
        return jsonify({'success': False, 'message': '金额格式错误'})
    
    try:
        unit_cost = float(unit_cost) if unit_cost else 0
    except:
        unit_cost = 0
    
    try:
        conn = sqlite3.connect(str(DB_FILE))
        c = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 兼容低版本 SQLite：手动判断更新或插入
        c.execute('SELECT id FROM cost_data WHERE cost_date = ? AND platform = ?', (cost_date, platform))
        existing = c.fetchone()
        if existing:
            c.execute('''
                UPDATE cost_data SET amount = ?, unit_cost = ?, created_at = ? WHERE id = ?
            ''', (amount, unit_cost, now, existing[0]))
        else:
            c.execute('''
                INSERT INTO cost_data (cost_date, platform, amount, unit_cost, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (cost_date, platform, amount, unit_cost, now))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'{platform} {cost_date} 成本录入成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': '录入失败: ' + str(e)})

# ─────────────────────────────────────────────
# 获取成本数据 API
# ─────────────────────────────────────────────
@app.route('/api/cost', methods=['GET'])
def get_cost():
    user = session.get('user')
    if not user or user['role'] != 'admin':
        return jsonify({'error': '无权限'}), 401
    
    cost_data = load_cost_data()
    return jsonify({'cost_data': cost_data})

# ─────────────────────────────────────────────
# 删除成本记录 API（管理员）
# ─────────────────────────────────────────────
@app.route('/api/cost/delete', methods=['POST'])
def delete_cost():
    user = session.get('user')
    if not user or user['role'] != 'admin':
        return jsonify({'success': False, 'message': '只有管理员可以删除成本'}), 401
    
    data = request.json
    cost_date = data.get('cost_date', '').strip()
    platform = data.get('platform', '').strip()
    
    if not cost_date or not platform:
        return jsonify({'success': False, 'message': '请提供日期和平台'})
    
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('DELETE FROM cost_data WHERE cost_date = ? AND platform = ?', (cost_date, platform))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    
    if deleted > 0:
        return jsonify({'success': True, 'message': f'已删除 {platform} {cost_date} 的成本记录'})
    else:
        return jsonify({'success': False, 'message': '未找到该记录'})

# ─────────────────────────────────────────────
# 招商员更新线索详情
# ─────────────────────────────────────────────
@app.route('/api/leads/update', methods=['POST'])
def update_lead():
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    data = request.json
    phone = data.get('phone', '').strip()
    
    # 检查是否是该招商员的线索
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('SELECT id, agent FROM new_leads WHERE phone = ?', (phone,))
    row = c.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'success': False, 'message': '线索不存在'})
    
    lead_id, lead_agent = row
    
    # 管理员可以更新所有，招商员只能更新自己的
    if user['role'] != 'admin' and lead_agent != user['name']:
        conn.close()
        return jsonify({'success': False, 'message': '无权修改此线索'})

    # 更新所有字段
    c.execute('''
        UPDATE new_leads SET
            name = ?, city = ?, validity = ?, region = ?, can_wechat = ?, remark = ?,
            entry_date = ?, 二次联系时间 = ?, 二次联系备注 = ?, 最近一次电联时间 = ?, 到访时间 = ?, 签约时间 = ?
        WHERE id = ?
    ''', (
        data.get('name', ''),
        data.get('city', ''),
        data.get('validity', ''),
        data.get('region', ''),
        data.get('can_wechat', ''),
        data.get('remark', ''),
        data.get('entry_date', ''),
        data.get('二次联系时间', ''),
        data.get('二次联系备注', ''),
        data.get('最近一次电联时间', ''),
        data.get('到访时间', ''),
        data.get('签约时间', ''),
        lead_id
    ))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': '更新成功'})

# ─────────────────────────────────────────────
# 删除线索
# ─────────────────────────────────────────────
@app.route('/api/leads/delete', methods=['POST'])
def delete_lead():
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({'success': False, 'message': '请求数据为空'})
        phone = str(data.get('phone', '')).strip()
        if not phone:
            return jsonify({'success': False, 'message': '手机号不能为空'})
    except Exception as e:
        return jsonify({'success': False, 'message': '请求解析失败: ' + str(e)})

    try:
        conn = sqlite3.connect(str(DB_FILE))
        c = conn.cursor()
        c.execute('SELECT id, agent FROM new_leads WHERE phone = ?', (phone,))
        row = c.fetchone()

        if not row:
            conn.close()
            return jsonify({'success': False, 'message': '线索不存在或无法删除（仅支持删除手动录入的线索）'})

        lead_id, lead_agent = row

        # 管理员可以删除所有，招商员只能删除自己的
        if user['role'] != 'admin' and lead_agent != user['name']:
            conn.close()
            return jsonify({'success': False, 'message': '无权删除此线索'})

        c.execute('DELETE FROM new_leads WHERE id = ?', (lead_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': '删除成功'})
    except Exception as e:
        return jsonify({'success': False, 'message': '删除出错: ' + str(e)})

# ─────────────────────────────────────────────
# 批量删除线索
# ─────────────────────────────────────────────
@app.route('/api/leads/batch-delete', methods=['POST'])
def batch_delete_leads():
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'message': '请先登录'}), 401

    try:
        data = request.get_json(force=True)
        phones = data.get('phones', [])
        if not phones or not isinstance(phones, list):
            return jsonify({'success': False, 'message': '请提供要删除的手机号列表'})
    except Exception as e:
        return jsonify({'success': False, 'message': '请求解析失败: ' + str(e)})

    try:
        conn = sqlite3.connect(str(DB_FILE))
        c = conn.cursor()

        deleted = 0
        skipped = 0
        for phone in phones:
            phone = str(phone).strip()
            if not phone:
                skipped += 1
                continue

            c.execute('SELECT id, agent FROM new_leads WHERE phone = ?', (phone,))
            row = c.fetchone()
            if not row:
                skipped += 1
                continue

            lead_id, lead_agent = row
            # 权限检查
            if user['role'] != 'admin' and lead_agent != user['name']:
                skipped += 1
                continue

            c.execute('DELETE FROM new_leads WHERE id = ?', (lead_id,))
            deleted += 1

        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'批量删除完成：成功 {deleted} 条，跳过 {skipped} 条'})
    except Exception as e:
        return jsonify({'success': False, 'message': '删除出错: ' + str(e)})

# ─────────────────────────────────────────────
# 标记新线索为已读
# ─────────────────────────────────────────────
@app.route('/api/leads/mark_read', methods=['POST'])
def mark_lead_read():
    user = session.get('user')
    if not user:
        return jsonify({'success': False, 'message': '请先登录'}), 401
    
    data = request.json
    lead_id = data.get('id')
    
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('UPDATE new_leads SET is_read = 1 WHERE id = ?', (lead_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

# ─────────────────────────────────────────────
# 获取未读提示
# ─────────────────────────────────────────────
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    user = session.get('user')
    if not user:
        return jsonify({'error': '请先登录'}), 401
    
    if user['role'] == 'admin':
        new_leads = load_new_leads()
        unread = [l for l in new_leads if l.get('是否已读', 1) == 0]
        return jsonify({'unread_count': len(unread), 'notifications': unread})
    
    agent_name = user['name']
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('SELECT * FROM new_leads WHERE agent = ? AND is_read = 0 ORDER BY created_at DESC', (agent_name,))
    rows = c.fetchall()
    conn.close()
    
    notifications = []
    for row in rows:
        notifications.append({
            'id': row[0],
            '手机号': row[1],
            '平台': row[2],
            '入库时间': row[10][:10] if row[10] else ''
        })
    
    return jsonify({'unread_count': len(notifications), 'notifications': notifications})

# ─────────────────────────────────────────────
# 导入Excel线索（管理员）— v3 完整字段版
# ─────────────────────────────────────────────
@app.route('/api/leads/import', methods=['POST'])
def import_leads():
    user = session.get('user')
    if not user or user['role'] != 'admin':
        return jsonify({'success': False, 'message': '只有管理员可以导入线索'}), 401

    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '请选择文件'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '请选择文件'})

    try:
        import pandas as pd
        from io import BytesIO

        file_bytes = file.read()
        filename = file.filename
        filename_lower = filename.lower()

        # ── 1) 读取Excel ──
        try:
            if filename_lower.endswith('.xls'):
                df = pd.read_excel(BytesIO(file_bytes), engine='xlrd')
            else:
                df = pd.read_excel(BytesIO(file_bytes), engine='openpyxl')
        except Exception as read_err:
            err_msg = str(read_err)
            if 'not supported' in err_msg.lower():
                err_msg += '（服务器缺少openpyxl库，请联系管理员安装: pip install openpyxl）'
            return jsonify({'success': False, 'message': f'读取Excel失败: {err_msg}'})

        if len(df) == 0:
            return jsonify({'success': False, 'message': 'Excel 文件为空（0行数据）'})

        cols = [str(c).strip() for c in df.columns]
        print(f"[导入] 文件={filename}, 行数={len(df)}, 列名={cols}")

        # ── 2) 智能识别列 ──
        def find_col(keywords):
            for kw in keywords:
                kw_lower = kw.lower()
                for col in cols:
                    if kw_lower in col.lower():
                        return col
            return None

        phone_col    = find_col(['手机号', '手机号码', '电话', '联系电话', '手机', 'phone', '客户电话'])
        platform_col = find_col(['平台', '来源', '渠道', '来源平台'])
        agent_col    = find_col(['所属招商', '跟进员工', '负责人', '招商员', '员工', '分配'])
        date_col     = find_col(['入库日期', '录入日期', '日期', '入库时间', '录入时间'])
        name_col     = find_col(['姓名', '名字', '客户姓名', '联系人'])
        city_col     = find_col(['城市', '省份', '地区', '所在城市', '省'])
        validity_col = find_col(['线索有效性', '有效性', '客户类型', '等级'])
        wechat_col   = find_col(['是否能加上微信', '能否加微', '加微信', '微信'])
        remark_col   = find_col(['备注', '说明', '备注信息', '客户情况备注'])
        follow_time_col  = find_col(['二次联系时间', '跟进时间', '下次联系时间'])
        follow_note_col  = find_col(['二次联系备注', '跟进备注', '联系备注'])
        call_time_col    = find_col(['最近一次电联时间', '电联时间', '最近联系时间'])
        visit_time_col   = find_col(['到访时间', '到店时间', '来访时间'])
        sign_time_col    = find_col(['签约时间', '成交时间', '签约日期'])

        if not phone_col:
            return jsonify({'success': False,
                'message': f'无法识别手机号列。当前列名: {cols}'})

        print(f"[导入] 列映射: 手机={phone_col}, 平台={platform_col}, 招商={agent_col}, 日期={date_col}")

        # ── 3) 文件类型判断 ──
        is_zhaoshang = '招商' in filename
        is_douyin_kezi = '客资' in filename or ('抖音' in filename and not is_zhaoshang)

        # ── 4) 解析所有行 ──
        def get_val(row, col):
            if not col:
                return ''
            v = row.get(col, '')
            if pd.isna(v):
                return ''
            s = str(v).strip()
            return s if s.lower() != 'nan' else ''

        def parse_date(row, col):
            if not col:
                return ''
            v = row.get(col)
            if pd.isna(v):
                return ''
            try:
                return pd.to_datetime(v).strftime('%Y-%m-%d')
            except:
                return ''

        parsed = []
        bad_rows = []
        for idx, row in df.iterrows():
            raw = row.get(phone_col, '')
            if pd.isna(raw):
                bad_rows.append({'row': int(idx)+2, 'raw': '空值', 'reason': '联系方式为空'})
                continue
            s = str(raw).strip()
            if not s or s.lower() == 'nan':
                bad_rows.append({'row': int(idx)+2, 'raw': '空值', 'reason': '联系方式为空'})
                continue

            digits = ''.join(filter(str.isdigit, s))
            if len(digits) == 11:
                phone = digits
            elif len(digits) >= 7:
                phone = digits
            else:
                phone = s  # 微信号保留

            # 入库日期：以Excel表格为准
            entry_date = parse_date(row, date_col)
            if not entry_date:
                for fc in ['日期', '时间', '创建日期', '添加日期']:
                    col = find_col([fc])
                    if col:
                        entry_date = parse_date(row, col)
                        if entry_date:
                            break
            if not entry_date:
                entry_date = datetime.now().strftime('%Y-%m-%d')

            # 招商员分配
            if is_douyin_kezi:
                agent = get_val(row, agent_col) or '郑建军'
            else:
                agent = get_val(row, find_col(['所属招商'])) or get_val(row, find_col(['跟进员工'])) or get_val(row, agent_col) or '郑建军'

            parsed.append({
                'phone': phone,
                'platform': get_val(row, platform_col) or '抖音',
                'agent': agent,
                'entry_date': entry_date,
                'name': get_val(row, name_col),
                'city': get_val(row, city_col),
                'validity': get_val(row, validity_col),
                'can_wechat': get_val(row, wechat_col),
                'remark': get_val(row, remark_col),
                'follow_time': parse_date(row, follow_time_col),
                'follow_note': get_val(row, follow_note_col),
                'call_time': parse_date(row, call_time_col),
                'visit_time': parse_date(row, visit_time_col),
                'sign_time': parse_date(row, sign_time_col),
            })

        if not parsed:
            return jsonify({'success': False, 'message': '未能解析出任何有效数据'})

        print(f"[导入] 解析成功: {len(parsed)} 条, 空值跳过: {len(bad_rows)} 条")

        # ── 5) 数据库写入 ──
        conn = sqlite3.connect(str(DB_FILE))
        c = conn.cursor()

        # 5.1) 清理已有重复
        c.execute('SELECT phone, COUNT(*) as cnt FROM new_leads GROUP BY phone HAVING cnt > 1')
        for phone, cnt in c.fetchall():
            c.execute('DELETE FROM new_leads WHERE phone = ? AND id NOT IN (SELECT MIN(id) FROM new_leads WHERE phone = ?)', (phone, phone))
        conn.commit()

        # 5.2) 加载已有线索
        c.execute('SELECT phone, platform, entry_date FROM new_leads')
        existing = {row[0]: {'platform': row[1], 'entry_date': row[2]} for row in c.fetchall()}

        added, updated, dup_skip = 0, 0, 0
        seen_in_file = set()

        for item in parsed:
            phone = item['phone']
            if phone in seen_in_file:
                dup_skip += 1
                continue
            seen_in_file.add(phone)

            platform = item['platform']
            agent = item['agent']
            entry_date = item['entry_date']

            if phone in existing:
                old = existing[phone]
                # 招商线索管理表导入时，抖音/小红书入库日期不变
                if is_zhaoshang and old['platform'] in ('抖音', '小红书'):
                    entry_date = old['entry_date']

                # UPDATE 全部字段
                c.execute('''UPDATE new_leads SET
                    platform = ?, agent = ?, entry_date = ?, name = ?,
                    city = ?, validity = ?, can_wechat = ?, remark = ?,
                    二次联系时间 = ?, 二次联系备注 = ?, 最近一次电联时间 = ?, 到访时间 = ?, 签约时间 = ?
                    WHERE phone = ?''', (
                    platform, agent, entry_date, item['name'],
                    item['city'], item['validity'], item['can_wechat'], item['remark'],
                    item['follow_time'], item['follow_note'], item['call_time'],
                    item['visit_time'], item['sign_time'], phone))
                updated += 1
            else:
                # INSERT 新线索
                c.execute('''INSERT INTO new_leads
                    (phone, platform, agent, entry_date, name, city, validity,
                     can_wechat, remark, created_at,
                     二次联系时间, 二次联系备注, 最近一次电联时间, 到访时间, 签约时间)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                    phone, platform, agent, entry_date, item['name'], item['city'],
                    item['validity'], item['can_wechat'], item['remark'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    item['follow_time'], item['follow_note'], item['call_time'],
                    item['visit_time'], item['sign_time']))
                added += 1
                existing[phone] = {'platform': platform, 'entry_date': entry_date}

        conn.commit()
        conn.close()

        msg = f'导入完成！新增 {added} 条，更新 {updated} 条'
        if dup_skip:
            msg += f'，Excel内重复跳过 {dup_skip} 条'
        if bad_rows:
            msg += f'，空值跳过 {len(bad_rows)} 条'

        return jsonify({
            'success': True, 'message': msg,
            'added': added, 'updated': updated,
            'dup_skip': dup_skip, 'bad': len(bad_rows),
            'bad_rows': bad_rows[:5]
        })

    except Exception as e:
        import traceback
        print(f"[导入错误] {str(e)}\n{traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'导入失败: {str(e)}'})

# ─────────────────────────────────────────────
# 管理员页面（包含线索录入表单）
# ─────────────────────────────────────────────
@app.route('/admin', methods=['GET'])
def admin_page():
    user = session.get('user')
    if not user or user['role'] != 'admin':
        return '<h1>只有管理员可以访问</h1><a href="/">返回</a>'
    
    # 获取招商员列表
    users = load_users()
    agents = [a['name'] for a in users.get('agents', [])]
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>线索录入 - 管理后台</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f7fa; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
            .header h1 { font-size: 24px; }
            .nav { display: flex; gap: 15px; }
            .nav a { color: white; text-decoration: none; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 8px; }
            .nav a:hover { background: rgba(255,255,255,0.3); }
            .container { background: white; border-radius: 12px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h2 { margin-bottom: 20px; color: #333; }
            .form { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; max-width: 800px; }
            .form-group { display: flex; flex-direction: column; }
            .form-group label { font-size: 14px; color: #666; margin-bottom: 5px; }
            .form-group input, .form-group select { padding: 10px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; }
            .form-group input:focus, .form-group select:focus { outline: none; border-color: #667eea; }
            .btn { grid-column: 1 / -1; padding: 14px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 10px; }
            .btn:hover { opacity: 0.9; }
            .message { margin-top: 15px; padding: 15px; border-radius: 8px; display: none; }
            .message.success { background: #d4edda; color: #155724; }
            .message.error { background: #f8d7da; color: #721c24; }
            .back-link { display: inline-block; margin-bottom: 20px; color: #667eea; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📝 线索录入 - 管理后台</h1>
            <div class="nav">
                <a href="/">返回看板</a>
                <a href="/">看板首页</a>
            </div>
        </div>
        <div class="container">
            <a href="/" class="back-link">← 返回看板</a>
            <h2>录入新线索</h2>
            <form class="form" id="leadForm">
                <div class="form-group">
                    <label>手机号 *</label>
                    <input type="text" id="phone" required placeholder="请输入手机号">
                </div>
                <div class="form-group">
                    <label>线索平台 *</label>
                    <select id="platform" required>
                        <option value="">请选择</option>
                        <option value="400线索">400线索</option>
                        <option value="小红书">小红书</option>
                        <option value="转介绍">转介绍</option>
                        <option value="豆包">豆包</option>
                        <option value="其他">其他</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>录入日期 *</label>
                    <input type="date" id="entry_date" required value="''' + datetime.now().strftime('%Y-%m-%d') + '''">
                </div>
                <div class="form-group">
                    <label>分配给 *</label>
                    <select id="agent" required>
                        <option value="">请选择招商员</option>
                        ''' + '\n'.join([f'<option value="{a}">{a}</option>' for a in agents]) + '''
                    </select>
                </div>
                <button type="submit" class="btn">录入线索</button>
            </form>
            <div class="message" id="message"></div>
        </div>

        <div class="container" style="margin-top:20px">
            <h2>📊 Excel 批量导入线索</h2>
            <div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:16px 20px;margin-bottom:16px;font-size:13px;color:#166534;line-height:1.7">
                <div style="font-weight:700;margin-bottom:4px">&#128161; 导入说明</div>
                <div>• 支持 .xlsx / .xls 格式，会自动识别"手机号"、"电话"等列</div>
                <div>• 文件名含 <b>"招商"</b> → 抖音/小红书已存在线索的<b>入库日期不修改</b></div>
                <div>• 已存在手机号 → <b>更新</b>其他信息；新手机号 → <b>新增</b></div>
            </div>
            <form id="importForm">
                <div class="form-group">
                    <label>选择 Excel 文件 <span style="color:#999;font-weight:400">（.xlsx / .xls）</span></label>
                    <input type="file" id="excelFile" accept=".xlsx,.xls" required style="padding:8px;border:2px solid #e0e0e0;border-radius:8px">
                </div>
                <button type="submit" class="btn" id="importBtn" style="background:linear-gradient(135deg,#10b981,#059669)">导入线索</button>
            </form>
            <div class="message" id="importMessage"></div>
            <div id="importResult" style="margin-top:15px;display:none"></div>
        </div>

        <script>
            document.getElementById('leadForm').onsubmit = async (e) => {
                e.preventDefault();
                const res = await fetch('/api/leads/add', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        phone: document.getElementById('phone').value,
                        platform: document.getElementById('platform').value,
                        entry_date: document.getElementById('entry_date').value,
                        agent: document.getElementById('agent').value
                    })
                });
                const data = await res.json();
                const msg = document.getElementById('message');
                msg.style.display = 'block';
                msg.className = 'message ' + (data.success ? 'success' : 'error');
                msg.textContent = data.message;
                if (data.success) {
                    document.getElementById('phone').value = '';
                }
            };

            document.getElementById('importForm').onsubmit = async (e) => {
                e.preventDefault();
                const fileInput = document.getElementById('excelFile');
                const btn = document.getElementById('importBtn');
                const msgBox = document.getElementById('importMessage');
                const resultBox = document.getElementById('importResult');

                if (!fileInput.files[0]) {
                    msgBox.style.display = 'block';
                    msgBox.className = 'message error';
                    msgBox.textContent = '请选择Excel文件';
                    return;
                }

                btn.disabled = true;
                btn.textContent = '正在导入...';
                msgBox.style.display = 'none';
                resultBox.style.display = 'none';

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                try {
                    const res = await fetch('/api/leads/import', { method: 'POST', body: formData });
                    const data = await res.json();

                    msgBox.style.display = 'block';
                    msgBox.className = 'message ' + (data.success ? 'success' : 'error');
                    msgBox.textContent = data.message;

                    if (data.success) {
                        fileInput.value = '';
                        // 显示统计卡片
                        let html = '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:10px">';
                        html += '<div style="background:#d4edda;border-radius:10px;padding:15px;text-align:center"><div style="font-size:24px;font-weight:700;color:#155724">' + (data.added || 0) + '</div><div style="font-size:13px;color:#155724">新增</div></div>';
                        html += '<div style="background:#fff3cd;border-radius:10px;padding:15px;text-align:center"><div style="font-size:24px;font-weight:700;color:#856404">' + (data.updated || 0) + '</div><div style="font-size:13px;color:#856404">更新</div></div>';
                        html += '<div style="background:#f8d7da;border-radius:10px;padding:15px;text-align:center"><div style="font-size:24px;font-weight:700;color:#721c24">' + (data.bad || 0) + '</div><div style="font-size:13px;color:#721c24">无法识别</div></div>';
                        html += '</div>';

                        // 显示失败详情
                        if (data.bad_rows && data.bad_rows.length) {
                            html += '<div style="margin-top:15px"><div style="font-weight:700;margin-bottom:8px;color:#721c24">前几条识别失败详情：</div>';
                            html += '<table style="width:100%;border-collapse:collapse;font-size:13px"><thead><tr style="background:#f8d7da"><th style="padding:8px;border:1px solid #f5c6cb">Excel行号</th><th style="padding:8px;border:1px solid #f5c6cb">原始值</th><th style="padding:8px;border:1px solid #f5c6cb">原因</th></tr></thead><tbody>';
                            data.bad_rows.forEach(r => {
                                html += '<tr><td style="padding:8px;border:1px solid #f5c6cb;text-align:center">' + r.row + '</td><td style="padding:8px;border:1px solid #f5c6cb">' + (r.raw || '') + '</td><td style="padding:8px;border:1px solid #f5c6cb">' + r.reason + '</td></tr>';
                            });
                            html += '</tbody></table></div>';
                        }

                        resultBox.innerHTML = html;
                        resultBox.style.display = 'block';
                    }
                } catch(err) {
                    msgBox.style.display = 'block';
                    msgBox.className = 'message error';
                    msgBox.textContent = '网络错误: ' + err;
                } finally {
                    btn.disabled = false;
                    btn.textContent = '导入线索';
                }
            };
        </script>
    </body>
    </html>
    '''
    return html

# ─────────────────────────────────────────────
# 主页
# ─────────────────────────────────────────────
@app.route('/', methods=['GET'])
def index():
    user = session.get('user')
    if not user:
        return login_page()
    
    user_name = user['name']
    role_text = '管理员' if user['role'] == 'admin' else '招商员'
    
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>线索看板</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f5f7fa; }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 20px 40px; display: flex; justify-content: space-between; align-items: center;
            }
            .header h1 { font-size: 24px; }
            .user-info { display: flex; align-items: center; gap: 20px; }
            .nav-links { display: flex; gap: 15px; }
            .nav-links a { color: white; text-decoration: none; padding: 8px 16px; background: rgba(255,255,255,0.2); border-radius: 8px; font-size: 14px; }
            .nav-links a:hover { background: rgba(255,255,255,0.3); }
            .badge { background: #ef4444; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; margin-left: 5px; }
            .logout-btn { 
                background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3);
                padding: 8px 20px; border-radius: 20px; cursor: pointer; font-size: 14px;
            }
            .logout-btn:hover { background: rgba(255,255,255,0.3); }
            .container { padding: 20px 40px; }
            iframe { width: 100%; height: calc(100vh - 100px); border: none; border-radius: 12px; background: white; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 线索看板</h1>
            <div class="user-info">
                <span>👤 ''' + user_name + ''' (''' + role_text + ''')</span>
                <div class="nav-links">
                    ''' + ('<a href="/admin">📝 录入线索</a>' if user['role'] == 'admin' else '') + '''
                </div>
                <button class="logout-btn" onclick="logout()">退出登录</button>
            </div>
        </div>
        <div class="container">
            <iframe src="/kanban_content"></iframe>
        </div>
        <script>
            async function logout() {
                await fetch('/api/logout', {method: 'POST'});
                window.location.href = '/';
            }
        </script>
    </body>
    </html>
    '''
    return html

# ─────────────────────────────────────────────
# 登录页面
# ─────────────────────────────────────────────
@app.route('/login', methods=['GET'])
def login_page():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>线索看板 - 登录</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .login-box {
                background: white;
                padding: 40px;
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                width: 380px;
            }
            h1 { text-align: center; color: #333; margin-bottom: 30px; font-size: 24px; }
            .input-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 8px; color: #666; font-size: 14px; }
            input { 
                width: 100%; padding: 12px 16px; border: 2px solid #e0e0e0;
                border-radius: 8px; font-size: 16px;
            }
            input:focus { outline: none; border-color: #667eea; }
            button { 
                width: 100%; padding: 14px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; border: none; border-radius: 8px;
                font-size: 16px; font-weight: 600; cursor: pointer;
            }
            button:hover { transform: translateY(-2px); }
            .error { color: #e74c3c; text-align: center; margin-top: 16px; font-size: 14px; }
            .demo { margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #999; }
            .demo h3 { font-size: 13px; margin-bottom: 10px; color: #666; }
            .demo p { margin: 5px 0; }
            code { background: #f5f5f5; padding: 2px 6px; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>🔐 线索看板登录</h1>
            <form id="loginForm">
                <div class="input-group">
                    <label>用户名</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div class="input-group">
                    <label>密码</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">登录</button>
                <div class="error" id="error"></div>
            </form>

        </div>
        <script>
            document.getElementById('loginForm').onsubmit = async (e) => {
                e.preventDefault();
                const res = await fetch('/api/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        username: document.getElementById('username').value,
                        password: document.getElementById('password').value
                    })
                });
                const data = await res.json();
                if (data.success) {
                    window.location.href = '/';
                } else {
                    document.getElementById('error').textContent = data.message;
                }
            };
        </script>
    </body>
    </html>
    '''

# ─────────────────────────────────────────────
# 看板内容（注入过滤后的数据）
# ─────────────────────────────────────────────
@app.route('/kanban_content', methods=['GET'])
def kanban_content():
    user = session.get('user')
    if not user:
        return '<h1>请先登录</h1><a href="/">返回登录</a>'
    
    html_file = BASE_DIR / '线索看板.html'
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    records = load_data()
    new_leads = load_new_leads()
    
    # 根据用户角色过滤数据
    if user['role'] == 'admin':
        filtered = records + new_leads
    else:
        agent_name = user['name']
        filtered = [r for r in records if r.get('所属招商', '') == agent_name 
                    or r.get('跟进员工', '') == agent_name]
        # 加上新录入的线索
        filtered += [r for r in new_leads if r.get('所属招商', '') == agent_name]
    
    # 统一按入库时间降序排列（最近日期在前）
    filtered.sort(key=lambda x: str(x.get('入库时间', '') or x.get('录入日期', '') or ''), reverse=True)
    
    # 替换原始数据
    pattern = r'window\.__ALL__\s*=\s*\[[\s\S]*?\];'
    replacement = 'window.__ALL__ = ' + json.dumps(filtered, ensure_ascii=False) + ';'
    content = re.sub(pattern, replacement, content, count=1)

    # 注入成本数据（从数据库实时读取，按平台区分）
    cost_data = load_cost_data()
    cost_by_plat = {'抖音': {}, '小红书': {}}
    all_days = set()
    for c in cost_data:
        d, plat, amt, uc = c['date'], c['platform'], c['amount'], c.get('unit_cost', 0)
        all_days.add(d)
        if plat not in cost_by_plat:
            cost_by_plat[plat] = {}
        cost_by_plat[plat][d] = {'spend': amt, 'unit_cost': uc if uc else 0, 'leads': 0}
    # 按平台计算单条成本（若数据库中未填写则自动计算）
    for plat in cost_by_plat:
        for d in cost_by_plat[plat]:
            day_leads = len([r for r in filtered if str(r.get('入库时间', '')).startswith(d) and r.get('平台') == plat])
            cost_by_plat[plat][d]['leads'] = day_leads
            if cost_by_plat[plat][d]['unit_cost'] <= 0 and day_leads > 0 and cost_by_plat[plat][d]['spend'] > 0:
                cost_by_plat[plat][d]['unit_cost'] = round(cost_by_plat[plat][d]['spend'] / day_leads, 2)
    cost_days = sorted(all_days)
    cost_script = 'window.__COST_BY_PLAT__ = ' + json.dumps(cost_by_plat, ensure_ascii=False) + ';\nwindow.__COST_DAYS__ = ' + json.dumps(cost_days, ensure_ascii=False) + ';'
    content = re.sub(r'window\.__COST_BY_PLAT__\s*=\s*\{[\s\S]*?\};\s*window\.__COST_DAYS__\s*=\s*\[[\s\S]*?\];', cost_script, content, count=1)
    # 兼容旧变量（HTML 中已改为 COST_BY_PLAT，此行为保险保留）
    content = content.replace('window.__COST__', 'window.__COST_BY_PLAT__')

    # 注入用户信息和未读提醒
    unread_count = 0
    unread_leads = []
    if user['role'] != 'admin':
        conn = sqlite3.connect(str(DB_FILE))
        c = conn.cursor()
        c.execute('SELECT * FROM new_leads WHERE agent = ? AND is_read = 0', (user['name'],))
        rows = c.fetchall()
        conn.close()
        unread_count = len(rows)
        for row in rows:
            unread_leads.append({'id': row[0], '手机号': row[1], '平台': row[2], '入库时间': row[10][:10] if row[10] else ''})
    
    # 注入用户信息和提醒
    user_script = '<script>window.CURRENT_USER = ' + json.dumps(user) + '; window.UNREAD_LEADS = ' + json.dumps(unread_leads) + '; window.UNREAD_COUNT = ' + str(unread_count) + ';</script>'
    content = content.replace('</head>', user_script + '</head>')
    
    # 添加提醒弹窗样式和逻辑
    if user['role'] != 'admin' and unread_count > 0:
        alert_html = '''
        <div id="leadAlert" style="position:fixed;top:70px;right:20px;background:linear-gradient(135deg,#f59e0b,#ef4444);color:white;padding:20px;border-radius:12px;box-shadow:0 4px 20px rgba(0,0,0,0.3);z-index:9999;max-width:350px;display:none;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
                <strong style="font-size:16px;">🔔 新线索提醒</strong>
                <span id="alertClose" style="cursor:pointer;font-size:20px;padding:0 5px;">×</span>
            </div>
            <p style="margin-bottom:10px;">您有 <strong id="alertCount">''' + str(unread_count) + '''</strong> 条新线索待处理：</p>
            <div id="alertList"></div>
        </div>
        <script>
            (function() {
                var leads = window.UNREAD_LEADS || [];
                var count = window.UNREAD_COUNT || 0;
                if (count > 0) {
                    var alertDiv = document.getElementById('leadAlert');
                    var listDiv = document.getElementById('alertList');
                    leads.forEach(function(lead) {
                        listDiv.innerHTML += '<div style="background:rgba(255,255,255,0.2);padding:8px 10px;border-radius:6px;margin-top:8px;font-size:13px;">📱 ' + lead['手机号'] + '<br><span style="font-size:12px;">平台: ' + lead['平台'] + ' | ' + lead['入库时间'] + '</span></div>';
                    });
                    alertDiv.style.display = 'block';
                    document.getElementById('alertClose').onclick = function() {
                        alertDiv.style.display = 'none';
                        // 标记所有未读线索为已读
                        leads.forEach(function(lead) {
                            fetch('/api/leads/mark_read', {
                                method: 'POST',
                                headers: {'Content-Type': 'application/json'},
                                body: JSON.stringify({id: lead.id})
                            });
                        });
                    };
                }
            })();
        </script>
        '''
        content = content.replace('</body>', alert_html + '</body>')
    
    return content

if __name__ == '__main__':
    print("=" * 50)
    print("🔐 线索看板服务 v2 启动中...")
    print("📍 访问地址: http://localhost:5001")
    print("=" * 50)
    print("\n测试账号：")
    print("  管理员: admin / admin123")
    print("  招商员1: zhengjianjun / zjj001345")
    print("  招商员2: liurenjie / lrj001678")
    print()
    app.run(debug=False, port=5001, host='0.0.0.0')
