# =============================================================================
# app/__init__.py  -  THE APPLICATION FACTORY
# -----------------------------------------------------------------------------
# This file turns the "app" folder into a Python PACKAGE and holds the
# create_app() factory function.
#
# WHY A FACTORY (and not a global `app = Flask(__name__)`)?
#   * It builds the app inside a function, so we can create fresh copies with
#     different settings (e.g. a separate one for automated tests).
#   * It avoids circular imports: extensions (db, migrate) are defined in their
#     own file and only *attached* to the app here.
#   * It is the structure professional Flask projects use, which makes each
#     layer's responsibility easy to point at and defend.
# =============================================================================

from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config, ensure_database_exists
from .extensions import db, migrate


def create_app(config_class=Config):
    """Build, configure, and return a ready-to-run Flask application.

    Anything that needs `app` happens INSIDE this function. Calling it returns
    a fully wired app; nothing global is created at import time.
    """
    # 1) Create the bare Flask app. __name__ helps Flask locate this package.
    app = Flask(__name__)

    # 2) Load all settings (DB URI, etc.) from the Config class in one shot.
    app.config.from_object(config_class)

    # 3) Allow a separate frontend (e.g. a JS app on another port) to call us.
    CORS(app)

    # 4) Make sure the MySQL *database* (schema) itself exists before SQLAlchemy
    #    tries to connect to it. MySQL will not auto-create a missing database,
    #    so this saves a manual "CREATE DATABASE" step.
    ensure_database_exists()

    # 5) Attach the shared extensions to THIS app instance.
    #    init_app() is the factory-friendly way to bind extensions that were
    #    created (unbound) in extensions.py.
    db.init_app(app)
    migrate.init_app(app, db)

    # 6) Register the blueprint that holds all the Todo API routes.
    #    Importing here (inside the function) keeps imports one-directional and
    #    avoids circular-import problems.
    from .routes import todos_bp
    app.register_blueprint(todos_bp)

    # 7) A tiny home/health route so hitting the root URL confirms the app runs.
    @app.route("/")
    def index():
        return jsonify({
            "service": "Todo REST API",
            "status": "running",
            "endpoints": {
                "list":   "GET    /api/todos",
                "get":    "GET    /api/todos/<id>",
                "create": "POST   /api/todos",
                "replace":"PUT    /api/todos/<id>",
                "update": "PATCH  /api/todos/<id>",
                "delete": "DELETE /api/todos/<id>",
            },
        })

    return app
