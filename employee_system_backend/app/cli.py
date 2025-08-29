from .seed import seed_initial_roles

# PUBLIC_INTERFACE
def register_cli(app):
    """Register custom CLI commands for maintenance."""

    @app.cli.command("seed-roles")
    def seed_roles():
        """Seed default RBAC roles."""
        with app.app_context():
            seed_initial_roles()
            print("Seeded default roles.")
