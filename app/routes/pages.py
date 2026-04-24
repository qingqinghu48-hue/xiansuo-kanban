"""
页面路由蓝图
包含主页、登录页、管理员页、看板内容等页面路由
"""
import json
import sqlite3
import re
from datetime import datetime

from flask import Blueprint, session, render_template_string

from app.config import Config
from app.models.users import load_users
from app.models.leads import load_data, load_new_leads, load_cost_data
from app.utils import _html_escape

pages_bp = Blueprint("pages", __name__)

DB_FILE = Config.DB_FILE


@pages_bp.route("/", methods=["GET"])
def index():
    user = session.get("user")
    if not user:
        return login_page()

    user_name = user["name"]
    role_text = "管理员" if user["role"] == "admin" else "招商员"

    return render_template_string("""
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
                <span>👤 {{ user_name }} ({{ role_text }})</span>
                <div class="nav-links">
                    {% if is_admin %}<a href="/admin">📝 录入线索</a>{% endif %}
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
    """, user_name=user_name, role_text=role_text, is_admin=(user['role'] == 'admin'))


@pages_bp.route("/login", methods=["GET"])
def login_page():
    return """
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
    """


@pages_bp.route("/kanban_content", methods=["GET"])
def kanban_content():
    user = session.get("user")
    if not user:
        return '<h1>请先登录</h1><a href="/">返回登录</a>'

    # 使用新的模板路径：templates/dashboard.html
    html_file = Config.BASE_DIR / 'templates' / 'dashboard.html'
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    records = load_data()
    new_leads = load_new_leads()

    # 根据用户角色过滤数据
    if user['role'] == 'admin' or user['role'] == 'guest':
        filtered = records + new_leads
    else:
        agent_name = user['name']
        filtered = [r for r in records if r.get('所属招商', '') == agent_name
                    or r.get('跟进员工', '') == agent_name]
        filtered += [r for r in new_leads if r.get('所属招商', '') == agent_name]

    filtered.sort(key=lambda x: str(x.get('入库时间', '') or x.get('录入日期', '') or ''), reverse=True)

    # 替换原始数据
    pattern = r'window\.__ALL__\s*=\s*\[[\s\S]*?\];'
    replacement = 'window.__ALL__ = ' + json.dumps(filtered, ensure_ascii=False) + ';'
    content = re.sub(pattern, replacement, content, count=1)

    # 注入成本数据
    cost_data = load_cost_data()
    cost_by_plat = {'抖音': {}, '小红书': {}}
    all_days = set()
    for c in cost_data:
        d, plat, amt, uc = c['date'], c['platform'], c['amount'], c.get('unit_cost', 0)
        all_days.add(d)
        if plat not in cost_by_plat:
            cost_by_plat[plat] = {}
        cost_by_plat[plat][d] = {'spend': amt, 'unit_cost': uc if uc else 0, 'leads': 0}
    for plat in cost_by_plat:
        for d in cost_by_plat[plat]:
            day_leads = len([r for r in filtered if str(r.get('入库时间', '')).startswith(d) and r.get('平台') == plat])
            cost_by_plat[plat][d]['leads'] = day_leads
            if cost_by_plat[plat][d]['unit_cost'] <= 0 and day_leads > 0 and cost_by_plat[plat][d]['spend'] > 0:
                cost_by_plat[plat][d]['unit_cost'] = round(cost_by_plat[plat][d]['spend'] / day_leads, 2)
    cost_days = sorted(all_days)
    cost_script = 'window.__COST_BY_PLAT__ = ' + json.dumps(cost_by_plat, ensure_ascii=False) + ';\nwindow.__COST_DAYS__ = ' + json.dumps(cost_days, ensure_ascii=False) + ';'
    content = re.sub(r'window\.__COST_BY_PLAT__\s*=\s*\{[\s\S]*?\};\s*window\.__COST_DAYS__\s*=\s*\[[\s\S]*?\];', cost_script, content, count=1)
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

    user_script = '<script>window.CURRENT_USER = ' + json.dumps(user) + '; window.UNREAD_LEADS = ' + json.dumps(unread_leads) + '; window.UNREAD_COUNT = ' + str(unread_count) + ';</script>'
    content = content.replace('</head>', user_script + '</head>')

    # 添加提醒弹窗
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
            function _esc(s){ s=s==null?'':String(s); return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'); }
            (function() {
                var leads = window.UNREAD_LEADS || [];
                var count = window.UNREAD_COUNT || 0;
                if (count > 0) {
                    var alertDiv = document.getElementById('leadAlert');
                    var listDiv = document.getElementById('alertList');
                    leads.forEach(function(lead) {
                        listDiv.innerHTML += '<div style="background:rgba(255,255,255,0.2);padding:8px 10px;border-radius:6px;margin-top:8px;font-size:13px;">📱 ' + _esc(lead['手机号']) + '<br><span style="font-size:12px;">平台: ' + _esc(lead['平台']) + ' | ' + _esc(lead['入库时间']) + '</span></div>';
                    });
                    alertDiv.style.display = 'block';
                    document.getElementById('alertClose').onclick = function() {
                        alertDiv.style.display = 'none';
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


@pages_bp.route("/admin", methods=["GET"])
def admin_page():
    user = session.get("user")
    if not user or user['role'] != 'admin':
        return '<h1>只有管理员可以访问</h1><a href="/">返回</a>'

    users = load_users()
    agents = [a['name'] for a in users.get('agents', [])]

    return render_template_string("""
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
            .card-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }
            .card { background: white; border-radius: 12px; padding: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .card h3 { font-size: 16px; color: #333; margin-bottom: 12px; }
            .card-btn { display: inline-block; padding: 12px 20px; background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; border: none; border-radius: 8px; font-size: 14px; cursor: pointer; text-decoration: none; text-align: center; }
            .card-btn:hover { opacity: 0.9; }
            .card-btn.orange { background: linear-gradient(135deg, #f59e0b, #d97706); }
            .card-btn.red { background: linear-gradient(135deg, #ef4444, #dc2626); }
            .card-btn.pink { background: linear-gradient(135deg, #ec4899, #be185d); }
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
        <div class="container" style="margin-bottom:20px">
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
                    <input type="date" id="entry_date" required value="{{ today }}">
                </div>
                <div class="form-group">
                    <label>分配给 *</label>
                    <select id="agent" required>
                        <option value="">请选择招商员</option>
                        {% for a in agents %}<option value="{{ a }}">{{ a }}</option>{% endfor %}
                    </select>
                </div>
                <button type="submit" class="btn">录入线索</button>
            </form>
            <div class="message" id="message"></div>
        </div>
        <div class="container">
            <h2>⚡ 快速功能</h2>
            <div class="card-grid">
                <div class="card">
                    <h3>💰 录入成本</h3>
                    <p style="color:#666;font-size:13px;margin-bottom:12px">录入抖音/小红书每日营销成本</p>
                    <button type="button" class="card-btn orange" onclick="alert('请通过API调用 /api/cost/add')">打开成本录入</button>
                </div>
                <div class="card">
                    <h3>📥 导入招商表</h3>
                    <p style="color:#666;font-size:13px;margin-bottom:12px">批量导入招商线索管理表</p>
                    <button type="button" class="card-btn blue" onclick="alert('请通过API调用 /api/leads/import')">打开导入窗口</button>
                </div>
                <div class="card">
                    <h3>🔥 导入抖音客资</h3>
                    <p style="color:#666;font-size:13px;margin-bottom:12px">批量导入抖音渠道线索</p>
                    <button type="button" class="card-btn red" onclick="alert('请通过API调用 /api/leads/import-douyin')">打开导入窗口</button>
                </div>
                <div class="card">
                    <h3>💖 导入小红书</h3>
                    <p style="color:#666;font-size:13px;margin-bottom:12px">批量导入小红书渠道线索</p>
                    <button type="button" class="card-btn pink" onclick="alert('请通过API调用 /api/leads/import')">打开导入窗口</button>
                </div>
            </div>
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
            if (data.success) { document.getElementById('phone').value = ''; }
        };
        </script>
    </body>
    </html>
    """, today=datetime.now().strftime('%Y-%m-%d'), agents=agents)
