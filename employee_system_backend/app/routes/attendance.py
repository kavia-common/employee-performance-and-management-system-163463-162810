from datetime import datetime
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Attendance
from ..schemas import AttendanceSchema

blp = Blueprint(
    "Attendance",
    "attendance",
    url_prefix="/attendance",
    description="Attendance tracking APIs (manual, GPS, face)"
)

# PUBLIC_INTERFACE
@blp.route("/")
class AttendanceList(MethodView):
    """List or create attendance entries."""

    @blp.response(200, AttendanceSchema(many=True))
    @jwt_required()
    def get(self):
        """List current user's attendance records."""
        uid = get_jwt_identity()
        records = db.session.execute(
            db.select(Attendance).filter_by(user_id=uid, is_deleted=False).order_by(Attendance.date.desc())
        ).scalars().all()
        return records

    @blp.arguments(AttendanceSchema)
    @blp.response(201, AttendanceSchema)
    @jwt_required()
    def post(self, payload):
        """Create a manual attendance record."""
        uid = get_jwt_identity()
        payload["user_id"] = uid
        method = payload.get("method")
        if method not in ("manual", "gps", "face"):
            abort(400, message="Invalid method")
        att = Attendance(
            user_id=uid,
            date=payload.get("date") or datetime.utcnow().date(),
            check_in_time=payload.get("check_in_time") or datetime.utcnow(),
            method=method,
            latitude=payload.get("latitude"),
            longitude=payload.get("longitude"),
            face_ref=payload.get("face_ref"),
            notes=payload.get("notes"),
        )
        db.session.add(att)
        db.session.commit()
        return att


# PUBLIC_INTERFACE
@blp.route("/<int:attendance_id>/checkout")
class AttendanceCheckout(MethodView):
    """Check out for a specific attendance record."""

    @blp.response(200, AttendanceSchema)
    @jwt_required()
    def post(self, attendance_id: int):
        """Set checkout time now."""
        uid = get_jwt_identity()
        att = db.session.get(Attendance, attendance_id)
        if not att or att.is_deleted or att.user_id != uid:
            abort(404, message="Attendance not found")
        if att.check_out_time:
            abort(400, message="Already checked out")
        att.check_out_time = datetime.utcnow()
        db.session.commit()
        return att
