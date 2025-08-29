from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Notification, User
from ..schemas import NotificationSchema
from ..utils import rbac_required

blp = Blueprint(
    "Notifications",
    "notifications",
    url_prefix="/notifications",
    description="Notification and alert APIs"
)

# PUBLIC_INTERFACE
@blp.route("/")
class NotificationList(MethodView):
    """List and create notifications."""

    @blp.response(200, NotificationSchema(many=True))
    @jwt_required()
    def get(self):
        uid = get_jwt_identity()
        items = db.session.execute(
            db.select(Notification).filter_by(user_id=uid, is_deleted=False).order_by(Notification.created_at.desc())
        ).scalars().all()
        return items

    @blp.arguments(NotificationSchema)
    @blp.response(201, NotificationSchema)
    @jwt_required()
    @rbac_required(["manager", "super_admin"])
    def post(self, payload):
        """Managers and super admins can create notifications for any user."""
        user = db.session.get(User, payload["user_id"])
        if not user:
            abort(404, message="User not found")
        nt = Notification(
            user_id=payload["user_id"],
            title=payload["title"],
            message=payload["message"],
            level=payload.get("level", "info"),
            is_read=False,
        )
        db.session.add(nt)
        db.session.commit()
        return nt


# PUBLIC_INTERFACE
@blp.route("/<int:notification_id>/read")
class NotificationRead(MethodView):
    """Mark notification as read."""

    @blp.response(200, NotificationSchema)
    @jwt_required()
    def post(self, notification_id: int):
        uid = get_jwt_identity()
        nt = db.session.get(Notification, notification_id)
        if not nt or nt.is_deleted or nt.user_id != uid:
            abort(404, message="Notification not found")
        nt.is_read = True
        db.session.commit()
        return nt
