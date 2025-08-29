from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Meeting, meeting_participants, User
from ..schemas import MeetingSchema, MeetingParticipantSchema

blp = Blueprint(
    "Meetings",
    "meetings",
    url_prefix="/meetings",
    description="Meeting scheduler and calendar APIs"
)

# PUBLIC_INTERFACE
@blp.route("/")
class MeetingsList(MethodView):
    """List and create meetings."""

    @blp.response(200, MeetingSchema(many=True))
    @jwt_required()
    def get(self):
        uid = get_jwt_identity()
        # return meetings organized by me or I'm a participant
        q = db.select(Meeting).join(
            meeting_participants, Meeting.id == meeting_participants.c.meeting_id, isouter=True
        ).filter(
            (Meeting.organizer_id == uid) | (meeting_participants.c.user_id == uid),
            Meeting.is_deleted == False  # noqa
        ).distinct().order_by(Meeting.start_time.desc())
        items = db.session.execute(q).scalars().all()
        return items

    @blp.arguments(MeetingSchema)
    @blp.response(201, MeetingSchema)
    @jwt_required()
    def post(self, payload):
        uid = get_jwt_identity()
        mt = Meeting(
            organizer_id=uid,
            title=payload["title"],
            description=payload.get("description"),
            start_time=payload["start_time"],
            end_time=payload["end_time"],
            location=payload.get("location"),
            is_virtual=payload.get("is_virtual", False),
        )
        db.session.add(mt)
        db.session.commit()
        return mt


# PUBLIC_INTERFACE
@blp.route("/<int:meeting_id>")
class MeetingDetail(MethodView):
    """Update, delete, or get meeting."""

    @blp.response(200, MeetingSchema)
    @jwt_required()
    def get(self, meeting_id: int):
        uid = get_jwt_identity()
        mt = db.session.get(Meeting, meeting_id)
        if not mt or mt.is_deleted or (mt.organizer_id != uid and not _is_participant(uid, meeting_id)):
            abort(404, message="Meeting not found")
        return mt

    @blp.arguments(MeetingSchema)
    @blp.response(200, MeetingSchema)
    @jwt_required()
    def put(self, payload, meeting_id: int):
        uid = get_jwt_identity()
        mt = db.session.get(Meeting, meeting_id)
        if not mt or mt.is_deleted or mt.organizer_id != uid:
            abort(404, message="Meeting not found or not organizer")
        for k in ("title", "description", "start_time", "end_time", "location", "is_virtual"):
            if k in payload:
                setattr(mt, k, payload[k])
        db.session.commit()
        return mt

    @jwt_required()
    def delete(self, meeting_id: int):
        uid = get_jwt_identity()
        mt = db.session.get(Meeting, meeting_id)
        if not mt or mt.is_deleted or mt.organizer_id != uid:
            abort(404, message="Meeting not found or not organizer")
        mt.is_deleted = True
        db.session.commit()
        return {"message": "Deleted"}


def _is_participant(user_id: int, meeting_id: int) -> bool:
    row = db.session.execute(
        db.select(meeting_participants).filter_by(user_id=user_id, meeting_id=meeting_id)
    ).first()
    return bool(row)


# PUBLIC_INTERFACE
@blp.route("/<int:meeting_id>/participants")
class MeetingParticipants(MethodView):
    """Manage participants for a meeting."""

    @blp.response(200, MeetingParticipantSchema(many=True))
    @jwt_required()
    def get(self, meeting_id: int):
        rows = db.session.execute(
            db.select(meeting_participants).filter_by(meeting_id=meeting_id)
        ).all()
        return [{"meeting_id": r.meeting_id, "user_id": r.user_id} for r in rows]

    @blp.arguments(MeetingParticipantSchema)
    @jwt_required()
    def post(self, payload, meeting_id: int):
        uid = get_jwt_identity()
        mt = db.session.get(Meeting, meeting_id)
        if not mt or mt.is_deleted or mt.organizer_id != uid:
            abort(404, message="Meeting not found or not organizer")
        user = db.session.get(User, payload["user_id"])
        if not user:
            abort(404, message="User not found")
        # Avoid duplicates
        exists = db.session.execute(
            db.select(meeting_participants).filter_by(meeting_id=meeting_id, user_id=user.id)
        ).first()
        if exists:
            return {"message": "Already participant"}
        db.session.execute(meeting_participants.insert().values(meeting_id=meeting_id, user_id=user.id))
        db.session.commit()
        return {"message": "Added"}, 201

    @blp.arguments(MeetingParticipantSchema)
    @jwt_required()
    def delete(self, payload, meeting_id: int):
        uid = get_jwt_identity()
        mt = db.session.get(Meeting, meeting_id)
        if not mt or mt.is_deleted or mt.organizer_id != uid:
            abort(404, message="Meeting not found or not organizer")
        db.session.execute(
            meeting_participants.delete().where(
                meeting_participants.c.meeting_id == meeting_id,
                meeting_participants.c.user_id == payload["user_id"]
            )
        )
        db.session.commit()
        return {"message": "Removed"}
