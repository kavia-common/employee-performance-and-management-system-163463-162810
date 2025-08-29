from functools import wraps
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from .extensions import db
from .models import User

def paginate(query, page: int, per_page: int):
    """Paginate a SQLAlchemy query."""
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return {
        "meta": {
            "total": pagination.total,
            "total_pages": pagination.pages,
            "first_page": 1,
            "last_page": pagination.pages,
            "page": pagination.page,
            "previous_page": pagination.prev_num if pagination.has_prev else None,
            "next_page": pagination.next_num if pagination.has_next else None,
        },
        "items": pagination.items,
    }

# PUBLIC_INTERFACE
def rbac_required(roles=None):
    """Decorator to enforce RBAC based on user roles."""
    roles = roles or []
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identity = get_jwt_identity()
            user = db.session.get(User, identity)
            if not user or not user.is_active:
                from flask_smorest import abort
                abort(401, message="Invalid or inactive user")
            if roles and not any(r.name in roles for r in user.roles):
                from flask_smorest import abort
                abort(403, message="Insufficient permissions")
            return fn(*args, **kwargs)
        return wrapper
    return decorator
