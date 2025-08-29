from flask import Flask
from flask_cors import CORS
from flask_smorest import Api
from .config import DevelopmentConfig
from .extensions import db, migrate, jwt
from .routes.health import blp as health_blp
from .routes.auth import blp as auth_blp
from .routes.roles import blp as roles_blp
from .routes.attendance import blp as attendance_blp
from .routes.breaks_schedules import blp as breaks_schedules_blp
from .routes.meetings import blp as meetings_blp
from .routes.projects_tasks import blp as projects_tasks_blp
from .routes.leaves import blp as leaves_blp
from .routes.notifications import blp as notifications_blp
from .cli import register_cli

# PUBLIC_INTERFACE
def create_app(config_object=DevelopmentConfig):
    """Flask application factory to build the API with all modules and docs."""
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.config.from_object(config_object)

    # CORS
    CORS(app, resources={r"/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})

    # Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # API and docs
    api = Api(app)
    # Register blueprints
    api.register_blueprint(health_blp)
    api.register_blueprint(auth_blp)
    api.register_blueprint(roles_blp)
    api.register_blueprint(attendance_blp)
    api.register_blueprint(breaks_schedules_blp)
    api.register_blueprint(meetings_blp)
    api.register_blueprint(projects_tasks_blp)
    api.register_blueprint(leaves_blp)
    api.register_blueprint(notifications_blp)

    # CLI
    register_cli(app)

    return app


# Create default app for scripts like generate_openapi.py and run.py
app = create_app()
api = Api(app)
