from app.routes.auth import auth_bp
from app.routes.companies import companies_bp
from app.routes.dashboard import dashboard_bp


def register_routes(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(companies_bp)
    app.register_blueprint(dashboard_bp)
