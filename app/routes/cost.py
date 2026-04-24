"""
成本路由蓝图
"""

import sqlite3
from datetime import datetime

from flask import Blueprint, jsonify, request, session

from app.config import Config
from app.models.leads import load_cost_data

cost_bp = Blueprint("cost", __name__)

DB_FILE = Config.DB_FILE


@cost_bp.route("/api/cost", methods=["GET"])
def get_cost():
    user = session.get("user")
    if not user or user["role"] != "admin":
        return jsonify({"error": "无权限"}), 401

    cost_data = load_cost_data()
    return jsonify({"cost_data": cost_data})


@cost_bp.route("/api/cost/add", methods=["POST"])
def add_cost():
    user = session.get("user")
    if not user or user["role"] != "admin":
        return jsonify({"success": False, "message": "只有管理员可以录入成本"}), 401

    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"success": False, "message": "请求数据为空"})
    except Exception as e:
        return jsonify({"success": False, "message": "请求解析失败: " + str(e)})

    cost_date = str(data.get("cost_date", "")).strip()
    platform = str(data.get("platform", "")).strip()
    amount = data.get("amount", 0)
    unit_cost = data.get("unit_cost", 0)

    if not cost_date or not platform:
        return jsonify({"success": False, "message": "请填写日期和平台"})

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "金额格式错误"})

    try:
        unit_cost = float(unit_cost) if unit_cost else 0
    except (ValueError, TypeError):
        unit_cost = 0

    try:
        conn = sqlite3.connect(str(DB_FILE))
        c = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 兼容低版本 SQLite：手动判断更新或插入
        c.execute(
            "SELECT id FROM cost_data WHERE cost_date = ? AND platform = ?",
            (cost_date, platform),
        )
        existing = c.fetchone()
        if existing:
            c.execute(
                """
                UPDATE cost_data SET amount = ?, unit_cost = ?, created_at = ? WHERE id = ?
            """,
                (amount, unit_cost, now, existing[0]),
            )
        else:
            c.execute(
                """
                INSERT INTO cost_data (cost_date, platform, amount, unit_cost, created_at)
                VALUES (?, ?, ?, ?, ?)
            """,
                (cost_date, platform, amount, unit_cost, now),
            )

        conn.commit()
        conn.close()
        return jsonify(
            {"success": True, "message": f"{platform} {cost_date} 成本录入成功"}
        )
    except Exception as e:
        return jsonify({"success": False, "message": "录入失败: " + str(e)})


@cost_bp.route("/api/cost/delete", methods=["POST"])
def delete_cost():
    user = session.get("user")
    if not user or user["role"] != "admin":
        return jsonify({"success": False, "message": "只有管理员可以删除成本"}), 401

    data = request.json
    cost_date = data.get("cost_date", "").strip()
    platform = data.get("platform", "").strip()

    if not cost_date or not platform:
        return jsonify({"success": False, "message": "请提供日期和平台"})

    conn = sqlite3.connect(str(DB_FILE))
    c = conn.cursor()
    c.execute(
        "DELETE FROM cost_data WHERE cost_date = ? AND platform = ?",
        (cost_date, platform),
    )
    deleted = c.rowcount
    conn.commit()
    conn.close()

    if deleted > 0:
        return jsonify(
            {"success": True, "message": f"已删除 {platform} {cost_date} 的成本记录"}
        )
    else:
        return jsonify({"success": False, "message": "未找到该记录"})
