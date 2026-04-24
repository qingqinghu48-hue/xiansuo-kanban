"""
通知路由蓝图
"""

import sqlite3

from flask import Blueprint, jsonify, session

from app.config import Config
from app.models.leads import load_new_leads

notifications_bp = Blueprint("notifications", __name__)

DB_FILE = Config.DB_FILE


@notifications_bp.route("/api/notifications", methods=["GET"])
def get_notifications():
    user = session.get("user")
    if not user:
        return jsonify({"error": "请先登录"}), 401

    if user["role"] == "admin":
        new_leads = load_new_leads()
        unread = [l for l in new_leads if l.get("是否已读", 1) == 0]
        return jsonify({"unread_count": len(unread), "notifications": unread})

    agent_name = user["name"]
    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute(
        "SELECT * FROM new_leads WHERE agent = ? AND is_read = 0 ORDER BY created_at DESC",
        (agent_name,),
    )
    rows = c.fetchall()
    conn.close()

    notifications = []
    for row in rows:
        notifications.append(
            {
                "id": row[0],
                "手机号": row[1],
                "平台": row[2],
                "入库时间": row[10][:10] if row[10] else "",
            }
        )

    return jsonify({"unread_count": len(notifications), "notifications": notifications})
