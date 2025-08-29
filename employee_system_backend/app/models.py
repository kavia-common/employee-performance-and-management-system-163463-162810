from datetime import datetime
from .extensions import db, TimestampMixin, SoftDeleteMixin

# Association table for many-to-many User<->Role
user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

class Role(TimestampMixin, SoftDeleteMixin, db.Model):
    """Role model for RBAC (e.g., super_admin, manager, team_lead, employee)."""
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255))


class User(TimestampMixin, SoftDeleteMixin, db.Model):
    """User model with multi-role support and profile fields."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(32))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime)

    roles = db.relationship("Role", secondary=user_roles, backref=db.backref("users", lazy="dynamic"))

    def has_role(self, role_name: str) -> bool:
        return any(r.name == role_name for r in self.roles)


class Attendance(TimestampMixin, SoftDeleteMixin, db.Model):
    """Attendance records supporting manual, gps, and face methods."""
    __tablename__ = "attendance"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    check_in_time = db.Column(db.DateTime)
    check_out_time = db.Column(db.DateTime)
    method = db.Column(db.String(16), nullable=False)  # manual|gps|face
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    face_ref = db.Column(db.String(255))  # reference to stored face image or embedding
    notes = db.Column(db.String(255))

    user = db.relationship("User", backref="attendance_records")


class Break(TimestampMixin, SoftDeleteMixin, db.Model):
    """Break sessions during workday."""
    __tablename__ = "breaks"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    type = db.Column(db.String(32), default="break")  # break|lunch|personal
    user = db.relationship("User", backref="breaks")


class Schedule(TimestampMixin, SoftDeleteMixin, db.Model):
    """Work schedule for users."""
    __tablename__ = "schedules"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0-6 (Mon-Sun)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    user = db.relationship("User", backref="schedules")


class Meeting(TimestampMixin, SoftDeleteMixin, db.Model):
    """Meeting entity with calendar fields."""
    __tablename__ = "meetings"
    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255))
    is_virtual = db.Column(db.Boolean, default=False, nullable=False)
    organizer = db.relationship("User", foreign_keys=[organizer_id], backref="organized_meetings")


meeting_participants = db.Table(
    "meeting_participants",
    db.Column("meeting_id", db.Integer, db.ForeignKey("meetings.id", ondelete="CASCADE"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Project(TimestampMixin, SoftDeleteMixin, db.Model):
    """Projects grouping tasks."""
    __tablename__ = "projects"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    owner = db.relationship("User", foreign_keys=[owner_id], backref="owned_projects")


class Task(TimestampMixin, SoftDeleteMixin, db.Model):
    """Task model with status and assignment."""
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="SET NULL"))
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(32), default="todo")  # todo|in_progress|done|blocked
    priority = db.Column(db.String(16), default="medium")  # low|medium|high|urgent
    due_date = db.Column(db.Date)
    assignee_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    project = db.relationship("Project", backref="tasks")
    assignee = db.relationship("User", foreign_keys=[assignee_id], backref="assigned_tasks")


class LeaveRequest(TimestampMixin, SoftDeleteMixin, db.Model):
    """Leave requests and approvals."""
    __tablename__ = "leave_requests"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(32), nullable=False)  # sick|vacation|personal|unpaid
    reason = db.Column(db.Text)
    status = db.Column(db.String(32), default="pending")  # pending|approved|rejected|cancelled
    approver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    user = db.relationship("User", foreign_keys=[user_id], backref="leave_requests")
    approver = db.relationship("User", foreign_keys=[approver_id], backref="approved_leaves")


class Notification(TimestampMixin, SoftDeleteMixin, db.Model):
    """Notification model for alerts and messages."""
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(16), default="info")  # info|warning|critical
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    user = db.relationship("User", backref="notifications")
