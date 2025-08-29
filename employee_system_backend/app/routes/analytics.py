from datetime import date
from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from ..extensions import db
from ..models import Attendance, Task, LeaveRequest, Notification
from ..utils import rbac_required

blp = Blueprint(
    "Analytics",
    "analytics",
    url_prefix="/analytics",
    description="Reports and analytics APIs"
)

# PUBLIC_INTERFACE
@blp.route("/attendance/summary")
class AttendanceSummary(MethodView):
    """Attendance summary counts."""

    @jwt_required()
    @rbac_required(["manager", "super_admin"])
    def get(self):
        today = date.today()
        total_today = db.session.execute(
            db.select(func.count(Attendance.id)).filter(func.date(Attendance.date) == today, Attendance.is_deleted == False)  # noqa
        ).scalar()
        methods = db.session.execute(
            db.select(Attendance.method, func.count(Attendance.id))
            .filter(func.date(Attendance.date) == today, Attendance.is_deleted == False)
            .group_by(Attendance.method)
        ).all()
        return {
            "total_today": total_today or 0,
            "by_method": {m[0]: m[1] for m in methods},
        }


# PUBLIC_INTERFACE
@blp.route("/tasks/status")
class TaskStatusCounts(MethodView):
    """Task status distribution."""

    @jwt_required()
    @rbac_required(["manager", "super_admin"])
    def get(self):
        rows = db.session.execute(
            db.select(Task.status, func.count(Task.id)).filter(Task.is_deleted == False).group_by(Task.status)  # noqa
        ).all()
        return {"by_status": {r[0]: r[1] for r in rows}}


# PUBLIC_INTERFACE
@blp.route("/leaves/pending")
class PendingLeaves(MethodView):
    """Pending leaves count."""

    @jwt_required()
    @rbac_required(["manager", "super_admin"])
    def get(self):
        cnt = db.session.execute(
            db.select(func.count(LeaveRequest.id)).filter(LeaveRequest.status == "pending", LeaveRequest.is_deleted == False)  # noqa
        ).scalar()
        return {"pending": cnt or 0}


# PUBLIC_INTERFACE
@blp.route("/notifications/unread")
class UnreadNotifications(MethodView):
    """Unread notifications count (system-level)."""

    @jwt_required()
    @rbac_required(["manager", "super_admin"])
    def get(self):
        cnt = db.session.execute(
            db.select(func.count(Notification.id)).filter(Notification.is_read == False, Notification.is_deleted == False)  # noqa
        ).scalar()
        return {"unread": cnt or 0}
