# Expose blueprints for registration in app factory
from .health import blp as health_blp  # noqa: F401
from .auth import blp as auth_blp  # noqa: F401
from .roles import blp as roles_blp  # noqa: F401
from .attendance import blp as attendance_blp  # noqa: F401
from .breaks_schedules import blp as breaks_schedules_blp  # noqa: F401
from .meetings import blp as meetings_blp  # noqa: F401
from .projects_tasks import blp as projects_tasks_blp  # noqa: F401
from .leaves import blp as leaves_blp  # noqa: F401
from .notifications import blp as notifications_blp  # noqa: F401
