from datetime import datetime
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from ..extensions import db
from ..models import User, Role
from ..schemas import UserCreateSchema, UserSchema, LoginSchema, TokenResponseSchema

blp = Blueprint(
    "Auth",
    "auth",
    url_prefix="/auth",
    description="Authentication and user management APIs"
)

# PUBLIC_INTERFACE
@blp.route("/register")
class Register(MethodView):
    """Register a new user with optional roles."""

    @blp.arguments(UserCreateSchema)
    @blp.response(201, UserSchema)
    def post(self, payload):
        """Register a new user.
        ---
        summary: Register user
        description: Create a new user and assign roles if provided. Roles must exist.
        """
        email = payload["email"].lower().strip()
        if db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none():
            abort(409, message="Email already registered")
        password_hash = generate_password_hash(payload["password"])
        user = User(
            email=email,
            password_hash=password_hash,
            first_name=payload.get("first_name"),
            last_name=payload.get("last_name"),
            phone=payload.get("phone"),
        )
        role_names = payload.get("roles") or []
        if role_names:
            roles = db.session.execute(db.select(Role).filter(Role.name.in_(role_names))).scalars().all()
            if len(roles) != len(set(role_names)):
                abort(400, message="One or more roles do not exist")
            user.roles.extend(roles)
        db.session.add(user)
        db.session.commit()
        return user


# PUBLIC_INTERFACE
@blp.route("/login")
class Login(MethodView):
    """Login to receive JWT tokens."""

    @blp.arguments(LoginSchema)
    @blp.response(200, TokenResponseSchema)
    def post(self, payload):
        """Login with email and password.
        ---
        summary: Login
        """
        email = payload["email"].lower().strip()
        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()
        if not user or not check_password_hash(user.password_hash, payload["password"]):
            abort(401, message="Invalid credentials")
        if not user.is_active:
            abort(403, message="User inactive")
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        access = create_access_token(identity=user.id, additional_claims={"roles": [r.name for r in user.roles]})
        refresh = create_refresh_token(identity=user.id)
        return {"access_token": access, "refresh_token": refresh, "user": user}


# PUBLIC_INTERFACE
@blp.route("/refresh")
class Refresh(MethodView):
    """Refresh access token using refresh token."""

    @blp.response(200, TokenResponseSchema)
    @jwt_required(refresh=True)
    def post(self):
        """Refresh token.
        ---
        summary: Refresh token
        """
        uid = get_jwt_identity()
        user = db.session.get(User, uid)
        if not user:
            abort(401, message="Invalid user")
        access = create_access_token(identity=user.id, additional_claims={"roles": [r.name for r in user.roles]})
        return {"access_token": access, "refresh_token": None, "user": user}


# PUBLIC_INTERFACE
@blp.route("/me")
class Me(MethodView):
    """Get current user profile."""

    @blp.response(200, UserSchema)
    @jwt_required()
    def get(self):
        """Get current user profile."""
        uid = get_jwt_identity()
        user = db.session.get(User, uid)
        if not user:
            abort(404, message="User not found")
        return user
