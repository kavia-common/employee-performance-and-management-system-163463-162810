from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Break, Schedule
from ..schemas import BreakSchema, ScheduleSchema

blp = Blueprint(
    "Breaks & Schedules",
    "breaks_schedules",
    url_prefix="/work",
    description="Break and schedule management APIs"
)

# PUBLIC_INTERFACE
@blp.route("/breaks")
class BreakList(MethodView):
    """List and create breaks."""

    @blp.response(200, BreakSchema(many=True))
    @jwt_required()
    def get(self):
        uid = get_jwt_identity()
        items = db.session.execute(db.select(Break).filter_by(user_id=uid, is_deleted=False)).scalars().all()
        return items

    @blp.arguments(BreakSchema)
    @blp.response(201, BreakSchema)
    @jwt_required()
    def post(self, payload):
        uid = get_jwt_identity()
        br = Break(
            user_id=uid,
            start_time=payload["start_time"],
            end_time=payload.get("end_time"),
            type=payload.get("type", "break"),
        )
        db.session.add(br)
        db.session.commit()
        return br


# PUBLIC_INTERFACE
@blp.route("/breaks/<int:break_id>")
class BreakDetail(MethodView):
    """Update or delete a break."""

    @blp.response(200, BreakSchema)
    @blp.arguments(BreakSchema)
    @jwt_required()
    def put(self, payload, break_id: int):
        uid = get_jwt_identity()
        br = db.session.get(Break, break_id)
        if not br or br.is_deleted or br.user_id != uid:
            abort(404, message="Break not found")
        for k in ("start_time", "end_time", "type"):
            if k in payload:
                setattr(br, k, payload[k])
        db.session.commit()
        return br

    @jwt_required()
    def delete(self, break_id: int):
        uid = get_jwt_identity()
        br = db.session.get(Break, break_id)
        if not br or br.is_deleted or br.user_id != uid:
            abort(404, message="Break not found")
        br.is_deleted = True
        db.session.commit()
        return {"message": "Deleted"}


# PUBLIC_INTERFACE
@blp.route("/schedules")
class ScheduleList(MethodView):
    """List and create schedules."""

    @blp.response(200, ScheduleSchema(many=True))
    @jwt_required()
    def get(self):
        uid = get_jwt_identity()
        items = db.session.execute(db.select(Schedule).filter_by(user_id=uid, is_deleted=False)).scalars().all()
        return items

    @blp.arguments(ScheduleSchema)
    @blp.response(201, ScheduleSchema)
    @jwt_required()
    def post(self, payload):
        uid = get_jwt_identity()
        sc = Schedule(
            user_id=uid,
            day_of_week=payload["day_of_week"],
            start_time=payload["start_time"],
            end_time=payload["end_time"],
        )
        db.session.add(sc)
        db.session.commit()
        return sc


# PUBLIC_INTERFACE
@blp.route("/schedules/<int:schedule_id>")
class ScheduleDetail(MethodView):
    """Update or delete schedule."""

    @blp.arguments(ScheduleSchema)
    @blp.response(200, ScheduleSchema)
    @jwt_required()
    def put(self, payload, schedule_id: int):
        uid = get_jwt_identity()
        sc = db.session.get(Schedule, schedule_id)
        if not sc or sc.is_deleted or sc.user_id != uid:
            abort(404, message="Schedule not found")
        for k in ("day_of_week", "start_time", "end_time"):
            if k in payload:
                setattr(sc, k, payload[k])
        db.session.commit()
        return sc

    @jwt_required()
    def delete(self, schedule_id: int):
        uid = get_jwt_identity()
        sc = db.session.get(Schedule, schedule_id)
        if not sc or sc.is_deleted or sc.user_id != uid:
            abort(404, message="Schedule not found")
        sc.is_deleted = True
        db.session.commit()
        return {"message": "Deleted"}
