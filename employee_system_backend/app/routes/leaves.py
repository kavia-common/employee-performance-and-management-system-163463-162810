from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import LeaveRequest
from ..schemas import LeaveRequestSchema
from ..utils import rbac_required

blp = Blueprint(
    "Leaves",
    "leaves",
    url_prefix="/leaves",
    description="Leave request and approval APIs"
)

# PUBLIC_INTERFACE
@blp.route("/")
class LeaveList(MethodView):
    """List and create leave requests."""

    @blp.response(200, LeaveRequestSchema(many=True))
    @jwt_required()
    def get(self):
        uid = get_jwt_identity()
        items = db.session.execute(
            db.select(LeaveRequest).filter_by(user_id=uid, is_deleted=False).order_by(LeaveRequest.created_at.desc())
        ).scalars().all()
        return items

    @blp.arguments(LeaveRequestSchema)
    @blp.response(201, LeaveRequestSchema)
    @jwt_required()
    def post(self, payload):
        uid = get_jwt_identity()
        lr = LeaveRequest(
            user_id=uid,
            start_date=payload["start_date"],
            end_date=payload["end_date"],
            type=payload["type"],
            reason=payload.get("reason"),
            status="pending",
        )
        db.session.add(lr)
        db.session.commit()
        return lr


# PUBLIC_INTERFACE
@blp.route("/<int:leave_id>")
class LeaveDetail(MethodView):
    """Get, update, cancel leave."""

    @blp.response(200, LeaveRequestSchema)
    @jwt_required()
    def get(self, leave_id: int):
        uid = get_jwt_identity()
        lr = db.session.get(LeaveRequest, leave_id)
        if not lr or lr.is_deleted or lr.user_id != uid:
            abort(404, message="Leave not found")
        return lr

    @blp.arguments(LeaveRequestSchema)
    @blp.response(200, LeaveRequestSchema)
    @jwt_required()
    def put(self, payload, leave_id: int):
        uid = get_jwt_identity()
        lr = db.session.get(LeaveRequest, leave_id)
        if not lr or lr.is_deleted or lr.user_id != uid:
            abort(404, message="Leave not found")
        if lr.status != "pending":
            abort(400, message="Only pending leaves can be updated")
        for k in ("start_date", "end_date", "type", "reason"):
            if k in payload:
                setattr(lr, k, payload[k])
        db.session.commit()
        return lr

    @jwt_required()
    def delete(self, leave_id: int):
        uid = get_jwt_identity()
        lr = db.session.get(LeaveRequest, leave_id)
        if not lr or lr.is_deleted or lr.user_id != uid:
            abort(404, message="Leave not found")
        lr.status = "cancelled"
        db.session.commit()
        return {"message": "Cancelled"}


# PUBLIC_INTERFACE
@blp.route("/<int:leave_id>/approve")
class LeaveApprove(MethodView):
    """Approve a leave request."""

    @blp.response(200, LeaveRequestSchema)
    @jwt_required()
    @rbac_required(["manager", "super_admin"])
    def post(self, leave_id: int):
        lr = db.session.get(LeaveRequest, leave_id)
        if not lr or lr.is_deleted:
            abort(404, message="Leave not found")
        if lr.status != "pending":
            abort(400, message="Only pending leaves can be approved")
        uid = get_jwt_identity()
        lr.status = "approved"
        lr.approver_id = uid
        db.session.commit()
        return lr


# PUBLIC_INTERFACE
@blp.route("/<int:leave_id>/reject")
class LeaveReject(MethodView):
    """Reject a leave request."""

    @blp.response(200, LeaveRequestSchema)
    @jwt_required()
    @rbac_required(["manager", "super_admin"])
    def post(self, leave_id: int):
        lr = db.session.get(LeaveRequest, leave_id)
        if not lr or lr.is_deleted:
            abort(404, message="Leave not found")
        if lr.status != "pending":
            abort(400, message="Only pending leaves can be rejected")
        uid = get_jwt_identity()
        lr.status = "rejected"
        lr.approver_id = uid
        db.session.commit()
        return lr
