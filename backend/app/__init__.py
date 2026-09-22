from flask import Flask
from flask_cors import CORS

from app.routes import register_routes


def create_app():
    app = Flask(__name__)

    CORS(app)

    @app.get("/api/health")
    def health():
        return {
            "status": "ok",
            "service": "Delyvo Logistics API"
        }

    register_routes(app)

    return app
