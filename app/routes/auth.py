"""
认证路由蓝图
"""

from flask import Blueprint, jsonify, request, session

from app.models.users import load_users

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "请输入用户名和密码"})

    users = load_users()

    if username == users["admin"]["username"] and password == users["admin"]["password"]:
        session["user"] = {
            "username": username,
            "name": users["admin"]["name"],
            "role": "admin",
        }
        return jsonify({"success": True, "name": users["admin"]["name"], "role": "admin"})

    for agent in users.get("agents", []):
        if agent["username"] == username and agent["password"] == password:
            session["user"] = {
                "username": username,
                "name": agent["name"],
                "role": "agent",
                "regions": agent.get("regions", []),
            }
            return jsonify({"success": True, "name": agent["name"], "role": "agent"})

    # 游客账号登录
    guest = users.get("guest")
    if guest and username == guest["username"] and password == guest["password"]:
        session["user"] = {
            "username": username,
            "name": guest["name"],
            "role": "guest",
        }
        return jsonify({"success": True, "name": guest["name"], "role": "guest"})

    return jsonify({"success": False, "message": "用户名或密码错误"})


@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@auth_bp.route("/api/current_user", methods=["GET"])
def current_user():
    user = session.get("user")
    if user:
        return jsonify({"logged_in": True, "user": user})
    return jsonify({"logged_in": False})
