from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from ..extensions import db
from ..models import Role
from ..schemas import RoleSchema
from ..utils import rbac_required

blp = Blueprint(
    "Roles",
    "roles",
    url_prefix="/roles",
    description="Role management (RBAC)"
)

# PUBLIC_INTERFACE
@blp.route("/")
class RoleList(MethodView):
    """List and create roles."""

    @blp.response(200, RoleSchema(many=True))
    @jwt_required()
    @rbac_required(["super_admin"])
    def get(self):
        """List roles."""
        roles = db.session.execute(db.select(Role).filter_by(is_deleted=False)).scalars().all()
        return roles

    @blp.arguments(RoleSchema)
    @blp.response(201, RoleSchema)
    @jwt_required()
    @rbac_required(["super_admin"])
    def post(self, payload):
        """Create role."""
        name = payload["name"].strip()
        if db.session.execute(db.select(Role).filter_by(name=name)).scalar_one_or_none():
            abort(409, message="Role exists")
        role = Role(name=name, description=payload.get("description"))
        db.session.add(role)
        db.session.commit()
        return role


# PUBLIC_INTERFACE
@blp.route("/<int:role_id>")
class RoleDetail(MethodView):
    """Get, update, delete role."""

    @blp.response(200, RoleSchema)
    @jwt_required()
    @rbac_required(["super_admin"])
    def get(self, role_id: int):
        role = db.session.get(Role, role_id)
        if not role or role.is_deleted:
            abort(404, message="Role not found")
        return role

    @blp.arguments(RoleSchema)
    @blp.response(200, RoleSchema)
    @jwt_required()
    @rbac_required(["super_admin"])
    def put(self, payload, role_id: int):
        role = db.session.get(Role, role_id)
        if not role or role.is_deleted:
            abort(404, message="Role not found")
        if "name" in payload:
            role.name = payload["name"]
        if "description" in payload:
            role.description = payload["description"]
        db.session.commit()
        return role

    @jwt_required()
    @rbac_required(["super_admin"])
    def delete(self, role_id: int):
        role = db.session.get(Role, role_id)
        if not role or role.is_deleted:
            abort(404, message="Role not found")
        role.is_deleted = True
        db.session.commit()
        return {"message": "Deleted"}
