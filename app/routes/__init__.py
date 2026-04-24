"""
蓝图注册中心
"""

from app.routes.auth import auth_bp
from app.routes.cost import cost_bp
from app.routes.leads import leads_bp
from app.routes.notifications import notifications_bp
from app.routes.pages import pages_bp


def register_blueprints(app):
    """将各蓝图注册到 Flask app"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(leads_bp)
    app.register_blueprint(cost_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(pages_bp)
