from marshmallow import Schema, fields, validate

# PUBLIC_INTERFACE
class PaginationSchema(Schema):
    """Metadata for paginated responses."""
    total = fields.Int()
    total_pages = fields.Int()
    first_page = fields.Int()
    last_page = fields.Int()
    page = fields.Int()
    previous_page = fields.Int(allow_none=True)
    next_page = fields.Int(allow_none=True)


# PUBLIC_INTERFACE
class RoleSchema(Schema):
    """Role serialization."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)


# PUBLIC_INTERFACE
class UserSchema(Schema):
    """User serialization without sensitive fields."""
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    roles = fields.List(fields.Nested(RoleSchema), dump_only=True)
    is_active = fields.Bool(dump_only=True)


# PUBLIC_INTERFACE
class UserCreateSchema(Schema):
    """User registration payload."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    first_name = fields.Str()
    last_name = fields.Str()
    phone = fields.Str()
    roles = fields.List(fields.Str(), description="List of role names to assign.")


# PUBLIC_INTERFACE
class LoginSchema(Schema):
    """Login payload."""
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


# PUBLIC_INTERFACE
class TokenResponseSchema(Schema):
    """JWT token response."""
    access_token = fields.Str()
    refresh_token = fields.Str()
    user = fields.Nested(UserSchema)


# PUBLIC_INTERFACE
class AttendanceSchema(Schema):
    """Attendance serialization."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    date = fields.Date()
    check_in_time = fields.DateTime(allow_none=True)
    check_out_time = fields.DateTime(allow_none=True)
    method = fields.Str(required=True, validate=validate.OneOf(["manual", "gps", "face"]))
    latitude = fields.Float(allow_none=True)
    longitude = fields.Float(allow_none=True)
    face_ref = fields.Str(allow_none=True)
    notes = fields.Str(allow_none=True)


# PUBLIC_INTERFACE
class BreakSchema(Schema):
    """Break serialization."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(allow_none=True)
    type = fields.Str(validate=validate.OneOf(["break", "lunch", "personal"]))


# PUBLIC_INTERFACE
class ScheduleSchema(Schema):
    """Schedule serialization."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    day_of_week = fields.Int(required=True, validate=validate.Range(min=0, max=6))
    start_time = fields.Time(required=True)
    end_time = fields.Time(required=True)


# PUBLIC_INTERFACE
class MeetingSchema(Schema):
    """Meeting serialization."""
    id = fields.Int(dump_only=True)
    organizer_id = fields.Int(allow_none=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    start_time = fields.DateTime(required=True)
    end_time = fields.DateTime(required=True)
    location = fields.Str(allow_none=True)
    is_virtual = fields.Bool()


# PUBLIC_INTERFACE
class MeetingParticipantSchema(Schema):
    """Meeting participant mapping."""
    meeting_id = fields.Int(required=True)
    user_id = fields.Int(required=True)


# PUBLIC_INTERFACE
class ProjectSchema(Schema):
    """Project serialization."""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    start_date = fields.Date(allow_none=True)
    end_date = fields.Date(allow_none=True)
    owner_id = fields.Int(allow_none=True)


# PUBLIC_INTERFACE
class TaskSchema(Schema):
    """Task serialization."""
    id = fields.Int(dump_only=True)
    project_id = fields.Int(allow_none=True)
    title = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    status = fields.Str(validate=validate.OneOf(["todo", "in_progress", "done", "blocked"]))
    priority = fields.Str(validate=validate.OneOf(["low", "medium", "high", "urgent"]))
    due_date = fields.Date(allow_none=True)
    assignee_id = fields.Int(allow_none=True)


# PUBLIC_INTERFACE
class LeaveRequestSchema(Schema):
    """Leave request serialization."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    type = fields.Str(required=True)
    reason = fields.Str(allow_none=True)
    status = fields.Str()
    approver_id = fields.Int(allow_none=True)


# PUBLIC_INTERFACE
class NotificationSchema(Schema):
    """Notification serialization."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    title = fields.Str(required=True)
    message = fields.Str(required=True)
    level = fields.Str(validate=validate.OneOf(["info", "warning", "critical"]))
    is_read = fields.Bool()
