# Test Suite for Employee System Backend

This directory contains a comprehensive pytest suite covering:
- Authentication and registration
- RBAC (roles endpoints)
- Attendance (create/list/checkout)
- Breaks and schedules
- Meetings and participants
- Projects and tasks
- Leaves and approvals/rejections
- Notifications and mark-as-read
- Analytics aggregates (RBAC protected)

How to run:
- Ensure dependencies installed: `pip install -r requirements.txt`
- Run in CI mode (non-interactive): `pytest -q`

The tests configure the app for testing with an in-memory SQLite database to avoid external dependencies.
