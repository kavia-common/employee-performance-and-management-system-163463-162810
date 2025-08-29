from app import create_app

app = create_app()

if __name__ == "__main__":
    # Do not hardcode host/port; can be set via env FLASK_RUN_PORT etc.
    app.run()
