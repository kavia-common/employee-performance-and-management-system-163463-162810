from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


class TimestampMixin:
    """Adds created_at and updated_at fields to models."""
    from sqlalchemy.sql import func
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())


class SoftDeleteMixin:
    """Adds soft deletion support."""
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
