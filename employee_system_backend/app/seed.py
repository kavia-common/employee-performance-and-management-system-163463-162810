from .extensions import db
from .models import Role

# PUBLIC_INTERFACE
def seed_initial_roles():
    """Seed default roles if they do not exist."""
    defaults = [
        {"name": "super_admin", "description": "Super administrator"},
        {"name": "manager", "description": "Manager/Supervisor"},
        {"name": "team_lead", "description": "Team lead"},
        {"name": "employee", "description": "Employee"},
    ]
    for r in defaults:
        existing = db.session.execute(db.select(Role).filter_by(name=r["name"])).scalar_one_or_none()
        if not existing:
            role = Role(name=r["name"], description=r["description"])
            db.session.add(role)
    db.session.commit()
