"""
线索看板后端服务 v2
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
            created_at TEXT NOT NULL,
            UNIQUE(cost_date, platform)
        )
    ''')
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
        leads.append({
            'id': row[0],
            '手机号': row[1],
            '平台': row[2],
            '所属招商': row[3],
            '录入日期': row[12] if len(row) > 12 and row[12] else '',
            '姓名': row[4] if len(row) > 4 else '',
            '省份': row[5] if len(row) > 5 else '',
            '线索有效性': row[6] if len(row) > 6 else '',
            '所属大区': row[7] if len(row) > 7 else '',
            '是否能加上微信': row[8] if len(row) > 8 else '',
            '备注': row[9] if len(row) > 9 else '',
            '入库时间': row[12] if len(row) > 12 and row[12] else (row[10][:10] if len(row) > 10 and row[10] else ''),
            '是否已读': row[11] if len(row) > 11 else 0,
            '二次联系时间': row[13] if len(row) > 13 else '',
            '二次联系备注': row[14] if len(row) > 14 else '',
            '最近一次电联时间': row[15] if len(row) > 15 else '',
            '到访时间': row[16] if len(row) > 16 else '',
            '签约时间': row[17] if len(row) > 17 else '',
            '来源文件': '手动录入'
        })
    return leads

# 加载成本数据
def load_cost_data():
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('SELECT cost_date, platform, amount FROM cost_data ORDER BY cost_date ASC')
    rows = c.fetchall()
    conn.close()
    return [{'date': r[0], 'platform': r[1], 'amount': r[2]} for r in rows]

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
    
    data = request.json
    cost_date = data.get('cost_date', '').strip()
    platform = data.get('platform', '').strip()
    amount = data.get('amount', 0)
    
    if not cost_date or not platform:
        return jsonify({'success': False, 'message': '请填写日期和平台'})
    
    try:
        amount = float(amount)
    except:
        return jsonify({'success': False, 'message': '金额格式错误'})
    
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 替换或插入（upsert）
    c.execute('''
        INSERT INTO cost_data (cost_date, platform, amount, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(cost_date, platform) DO UPDATE SET amount = ?, created_at = ?
    ''', (cost_date, platform, amount, now, amount, now))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': f'{platform} {cost_date} 成本录入成功'})

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

    data = request.json
    phone = data.get('phone', '').strip()

    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute('SELECT id, agent FROM new_leads WHERE phone = ?', (phone,))
    row = c.fetchone()

    if not row:
        conn.close()
        return jsonify({'success': False, 'message': '线索不存在'})

    lead_id, lead_agent = row

    # 管理员可以删除所有，招商员只能删除自己的
    if user['role'] != 'admin' and lead_agent != user['name']:
        conn.close()
        return jsonify({'success': False, 'message': '无权删除此线索'})

    c.execute('DELETE FROM new_leads WHERE id = ?', (lead_id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': '删除成功'})

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
# 导入Excel线索（管理员）
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

        # 读取 Excel（先保存文件内容，避免流被消耗）
        file_bytes = file.read()
        df = pd.read_excel(BytesIO(file_bytes), engine='openpyxl')

        # 调试：记录列名到日志
        print(f"[导入调试] 文件名: {file.filename}, 列名: {list(df.columns)}, 总行数: {len(df)}")

        # 根据文件名判断导入类型
        filename = file.filename
        is_zhaoshang = '招商线索管理表' in filename
        is_douyin_kezi = '客资' in filename or ('抖音' in filename and not is_zhaoshang)

        conn = sqlite3.connect(str(DB_FILE))
        c = conn.cursor()

        # 获取已有线索（phone -> platform, entry_date）
        c.execute('SELECT phone, platform, entry_date FROM new_leads')
        existing = {row[0]: {'platform': row[1] or '', 'entry_date': row[2] or ''} for row in c.fetchall()}

        added_count = 0
        updated_count = 0
        skipped_count = 0
        skip_reasons = []
        today = datetime.now().strftime('%Y-%m-%d')

        # 手机号列名候选（兼容多种命名）
        phone_cols = ['手机号', '手机号码', '电话', '联系电话', '手机', 'Phone', 'phone']
        # 平台列名候选
        platform_cols = ['平台', '来源平台', '渠道']
        # 招商员列名候选
        agent_cols = ['所属招商', '跟进员工', '招商员', '负责人', '分配']
        follow_cols = ['跟进员工', '负责人', '所属招商']
        # 日期列名候选
        date_cols = ['入库日期', '入库时间', '录入日期', '日期', '录入时间']
        # 姓名列名候选
        name_cols = ['姓名', '名字', '客户姓名', '联系人']
        # 城市列名候选
        city_cols = ['城市', '省份', '地区', '所在城市', '省']
        # 有效性列名候选
        validity_cols = ['有效性', '线索有效性', '客户类型', '等级']
        # 大区列名候选
        region_cols = ['所属大区', '大区', '区域', '所属区域']
        # 能否加微列名候选
        wechat_cols = ['能否加微', '是否能加上微信', '加微信', '微信']
        # 备注列名候选
        remark_cols = ['备注', '说明', '备注信息']

        def get_val(row, candidates, default=''):
            for col in candidates:
                if col in row and pd.notna(row[col]):
                    v = str(row[col]).strip()
                    if v and v != 'nan':
                        return v
            return default

        def get_phone(row):
            for col in phone_cols:
                if col in row:
                    v = row[col]
                    if isinstance(v, float):
                        if pd.isna(v) or v != v:
                            continue
                        # 处理 1.3193651186e+10 科学计数法
                        if v > 1e10:
                            return str(int(v))
                        v = str(int(v))
                    elif pd.isna(v):
                        continue
                    else:
                        v = str(v).strip()
                    # 清理手机号：去空格、去小数点、取数字
                    v = ''.join(filter(str.isdigit, v))
                    if len(v) >= 7:
                        return v
            return ''

        for idx, row in df.iterrows():
            try:
                phone = get_phone(row)
                if not phone:
                    skipped_count += 1
                    if idx < 3:
                        skip_reasons.append(f"第{idx+1}行: 无法识别手机号")
                    continue

                # 解析平台
                platform = get_val(row, platform_cols, '抖音')

                # 解析招商员
                if is_douyin_kezi:
                    agent = get_val(row, follow_cols, '郑建军')
                else:
                    agent = get_val(row, ['所属招商', '跟进员工'], '') or get_val(row, follow_cols, '郑建军')
                if not agent:
                    agent = '郑建军'

                # 解析入库日期
                entry_date = today
                for col in date_cols:
                    if col in row and pd.notna(row[col]):
                        try:
                            entry_date = pd.to_datetime(row[col]).strftime('%Y-%m-%d')
                            break
                        except:
                            pass

                # 解析其他字段
                name = get_val(row, name_cols)
                city = get_val(row, city_cols)
                validity = get_val(row, validity_cols)
                region = get_val(row, region_cols)
                can_wechat = get_val(row, wechat_cols)
                remark = get_val(row, remark_cols)

                if phone in existing:
                    # ── 已存在线索：UPDATE ──
                    old = existing[phone]
                    old_platform = old['platform']

                    # 入库日期更新规则：
                    # 招商线索管理表模式下，抖音/小红书平台的入库日期不修改
                    if is_zhaoshang and old_platform in ('抖音', '小红书'):
                        entry_date = old['entry_date']

                    c.execute('''
                        UPDATE new_leads SET
                            platform = ?, agent = ?, entry_date = ?, name = ?,
                            city = ?, validity = ?, region = ?, can_wechat = ?, remark = ?
                        WHERE phone = ?
                    ''', (platform, agent, entry_date, name, city, validity, region, can_wechat, remark, phone))
                    updated_count += 1
                else:
                    # ── 新线索：INSERT ──
                    c.execute('''
                        INSERT INTO new_leads (phone, platform, agent, entry_date, name, city, validity, region, can_wechat, remark, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (phone, platform, agent, entry_date, name, city, validity, region, can_wechat, remark, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                    existing[phone] = {'platform': platform, 'entry_date': entry_date}
                    added_count += 1

            except Exception as row_err:
                skipped_count += 1
                skip_reasons.append(f"第{idx+1}行: {str(row_err)[:50]}")
                continue

        conn.commit()
        conn.close()

        # 组装返回消息
        msg_parts = []
        if added_count:
            msg_parts.append(f'新增 {added_count} 条')
        if updated_count:
            msg_parts.append(f'更新 {updated_count} 条')
        if skipped_count:
            msg_parts.append(f'跳过 {skipped_count} 条')
        if not msg_parts:
            msg_parts.append('未导入任何数据')

        message = '，'.join(msg_parts)
        if skip_reasons:
            message += '。前几条跳过原因: ' + '; '.join(skip_reasons[:3])

        return jsonify({'success': True, 'message': message})

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
            <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:16px 20px;margin-bottom:20px;font-size:13px;color:#475569;line-height:1.8">
                <div style="font-weight:700;color:#1e293b;margin-bottom:8px;font-size:14px">📋 导入规则说明</div>
                <div style="margin-bottom:10px"><span style="background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:4px;font-weight:600">招商线索管理表</span> <span style="color:#94a3b8">（文件名包含"招商线索管理表"）</span></div>
                <ul style="margin:0 0 12px 18px;padding:0">
                    <li>已存在的线索 → <b>更新其他信息</b>，抖音/小红书平台的<b>入库日期保持不变</b></li>
                    <li>其他平台线索（400线索等）→ 所有信息以导入表为准，<b>包括入库日期</b></li>
                    <li>招商员分配：优先「所属招商」，其次「跟进员工」</li>
                </ul>
                <div style="margin-bottom:10px"><span style="background:#fce7f3;color:#be185d;padding:2px 8px;border-radius:4px;font-weight:600">抖音来客客资表</span> <span style="color:#94a3b8">（文件名包含"客资"或"抖音"）</span></div>
                <ul style="margin:0 0 0 18px;padding:0">
                    <li>按「跟进员工」直接分配账号（如郑建军 → 郑建军）</li>
                    <li>新线索新增，已存在线索更新全部信息</li>
                </ul>
            </div>
            <form id="importForm">
                <div class="form-group">
                    <label>选择 Excel 文件 <span style="color:#999;font-weight:400">（.xlsx / .xls）</span></label>
                    <input type="file" id="excelFile" accept=".xlsx,.xls" required style="padding:8px;border:2px solid #e0e0e0;border-radius:8px">
                </div>
                <button type="submit" class="btn" style="background:#10b981">导入线索</button>
            </form>
            <div class="message" id="importMessage"></div>
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
                if (!fileInput.files[0]) {
                    alert('请选择Excel文件');
                    return;
                }
                const formData = new FormData();
                formData.append('file', fileInput.files[0]);
                try {
                    const res = await fetch('/api/leads/import', { method: 'POST', body: formData });
                    const data = await res.json();
                    const msg = document.getElementById('importMessage');
                    msg.style.display = 'block';
                    msg.className = 'message ' + (data.success ? 'success' : 'error');
                    msg.textContent = data.message;
                    if (data.success) {
                        fileInput.value = '';
                    }
                } catch(err) {
                    alert('导入失败: ' + err);
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
    
    # 替换原始数据
    pattern = r'window\.__ALL__\s*=\s*\[[\s\S]*?\];'
    replacement = 'window.__ALL__ = ' + json.dumps(filtered, ensure_ascii=False) + ';'
    content = re.sub(pattern, replacement, content, count=1)

    # 注入成本数据（从数据库实时读取）
    cost_data = load_cost_data()
    cost_dict = {}
    for c in cost_data:
        d = c['date']
        if d not in cost_dict:
            cost_dict[d] = {'spend': 0, 'unit_cost': 0, 'leads': 0}
        cost_dict[d]['spend'] += c['amount']
    # 计算单条成本
    for d in cost_dict:
        day_leads = len([r for r in filtered if str(r.get('入库时间', '')).startswith(d) and r.get('平台') in ('抖音', '小红书')])
        cost_dict[d]['leads'] = day_leads
        if day_leads > 0 and cost_dict[d]['spend'] > 0:
            cost_dict[d]['unit_cost'] = round(cost_dict[d]['spend'] / day_leads, 2)
    cost_days = sorted(cost_dict.keys())
    cost_script = 'window.__COST__ = ' + json.dumps(cost_dict, ensure_ascii=False) + ';\nwindow.__COST_DAYS__ = ' + json.dumps(cost_days, ensure_ascii=False) + ';'
    content = re.sub(r'window\.__COST__\s*=\s*\{[\s\S]*?\};\s*window\.__COST_DAYS__\s*=\s*\[[\s\S]*?\];', cost_script, content, count=1)

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
