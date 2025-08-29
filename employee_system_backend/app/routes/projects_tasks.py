from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models import Project, Task
from ..schemas import ProjectSchema, TaskSchema

blp = Blueprint(
    "Projects & Tasks",
    "projects_tasks",
    url_prefix="/workitems",
    description="Project and task management APIs"
)

# PUBLIC_INTERFACE
@blp.route("/projects")
class ProjectList(MethodView):
    """List and create projects."""

    @blp.response(200, ProjectSchema(many=True))
    @jwt_required()
    def get(self):
        items = db.session.execute(
            db.select(Project).filter_by(is_deleted=False).order_by(Project.created_at.desc())
        ).scalars().all()
        return items

    @blp.arguments(ProjectSchema)
    @blp.response(201, ProjectSchema)
    @jwt_required()
    def post(self, payload):
        uid = get_jwt_identity()
        pr = Project(
            name=payload["name"],
            description=payload.get("description"),
            start_date=payload.get("start_date"),
            end_date=payload.get("end_date"),
            owner_id=payload.get("owner_id") or uid,
        )
        db.session.add(pr)
        db.session.commit()
        return pr


# PUBLIC_INTERFACE
@blp.route("/projects/<int:project_id>")
class ProjectDetail(MethodView):
    """Get, update, delete project."""

    @blp.response(200, ProjectSchema)
    @jwt_required()
    def get(self, project_id: int):
        pr = db.session.get(Project, project_id)
        if not pr or pr.is_deleted:
            abort(404, message="Project not found")
        return pr

    @blp.arguments(ProjectSchema)
    @blp.response(200, ProjectSchema)
    @jwt_required()
    def put(self, payload, project_id: int):
        pr = db.session.get(Project, project_id)
        if not pr or pr.is_deleted:
            abort(404, message="Project not found")
        for k in ("name", "description", "start_date", "end_date", "owner_id"):
            if k in payload:
                setattr(pr, k, payload[k])
        db.session.commit()
        return pr

    @jwt_required()
    def delete(self, project_id: int):
        pr = db.session.get(Project, project_id)
        if not pr or pr.is_deleted:
            abort(404, message="Project not found")
        pr.is_deleted = True
        db.session.commit()
        return {"message": "Deleted"}


# PUBLIC_INTERFACE
@blp.route("/tasks")
class TaskList(MethodView):
    """List and create tasks."""

    @blp.response(200, TaskSchema(many=True))
    @jwt_required()
    def get(self):
        items = db.session.execute(
            db.select(Task).filter_by(is_deleted=False).order_by(Task.created_at.desc())
        ).scalars().all()
        return items

    @blp.arguments(TaskSchema)
    @blp.response(201, TaskSchema)
    @jwt_required()
    def post(self, payload):
        ts = Task(
            project_id=payload.get("project_id"),
            title=payload["title"],
            description=payload.get("description"),
            status=payload.get("status", "todo"),
            priority=payload.get("priority", "medium"),
            due_date=payload.get("due_date"),
            assignee_id=payload.get("assignee_id"),
        )
        db.session.add(ts)
        db.session.commit()
        return ts


# PUBLIC_INTERFACE
@blp.route("/tasks/<int:task_id>")
class TaskDetail(MethodView):
    """Get, update, delete task."""

    @blp.response(200, TaskSchema)
    @jwt_required()
    def get(self, task_id: int):
        ts = db.session.get(Task, task_id)
        if not ts or ts.is_deleted:
            abort(404, message="Task not found")
        return ts

    @blp.arguments(TaskSchema)
    @blp.response(200, TaskSchema)
    @jwt_required()
    def put(self, payload, task_id: int):
        ts = db.session.get(Task, task_id)
        if not ts or ts.is_deleted:
            abort(404, message="Task not found")
        for k in ("project_id", "title", "description", "status", "priority", "due_date", "assignee_id"):
            if k in payload:
                setattr(ts, k, payload[k])
        db.session.commit()
        return ts

    @jwt_required()
    def delete(self, task_id: int):
        ts = db.session.get(Task, task_id)
        if not ts or ts.is_deleted:
            abort(404, message="Task not found")
        ts.is_deleted = True
        db.session.commit()
        return {"message": "Deleted"}
