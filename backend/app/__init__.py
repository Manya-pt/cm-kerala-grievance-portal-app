"""Flask application factory."""
import logging

from flask import Flask, jsonify
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .config import Config
from .models import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    logging.basicConfig(level=logging.INFO)

    origins = app.config["FRONTEND_ORIGIN"]
    CORS(app, resources={r"/api/*": {"origins": origins.split(",") if origins != "*" else "*"}})
    db.init_app(app)

    from .routes import admin_routes, auth_routes, grievance_routes, public_routes
    for module in (auth_routes, public_routes, grievance_routes, admin_routes):
        app.register_blueprint(module.bp)

    @app.after_request
    def security_headers(resp):
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return resp

    @app.errorhandler(HTTPException)
    def http_error(e):
        return jsonify(error=e.description), e.code

    @app.errorhandler(Exception)
    def server_error(e):
        app.logger.exception("Unhandled error")
        return jsonify(error="Something went wrong. Please try again."), 500

    @app.get("/")
    def root():
        return jsonify(name="CM Kerala Grievance Portal API (recruitment prototype)",
                       docs="See DOCUMENTATION/04_API_Documentation.md", health="/api/health")

    with app.app_context():
        db.create_all()  # creates tables if they don't exist
        if app.config["SEED_ON_START"]:
            from .seed import seed_if_empty
            seed_if_empty()

    return app
