from datetime import datetime, date, timezone
from .conftest import auth_headers

def setup_data_for_analytics(client, register_user, login_user):
    # Create employee and manager
    register_user("an_emp@example.com", "password123", roles=["employee"])
    register_user("an_mgr@example.com", "password123", roles=["manager"])

    emp_token = login_user("an_emp@example.com", "password123").get_json()["access_token"]
    mgr_token = login_user("an_mgr@example.com", "password123").get_json()["access_token"]

    # Employee creates attendance (manual)
    client.post("/attendance/", headers=auth_headers(emp_token), json={
        "user_id": 1, "method": "manual", "check_in_time": datetime.now(timezone.utc).isoformat()
    })
    # Employee creates a task
    client.post("/workitems/tasks", headers=auth_headers(emp_token), json={
        "title": "Do X", "status": "todo", "priority": "medium"
    })
    # Employee creates pending leave
    today = date.today()
    client.post("/leaves/", headers=auth_headers(emp_token), json={
        "user_id": 1, "start_date": today.isoformat(), "end_date": today.isoformat(), "type": "sick"
    })
    # Manager creates a notification for employee (unread)
    emp_id = 1
    client.post("/notifications/", headers=auth_headers(mgr_token), json={
        "user_id": emp_id, "title": "Alert", "message": "Test alert", "level": "info"
    })
    return emp_token, mgr_token


def test_analytics_requires_manager_or_super_admin(client, register_user, login_user):
    register_user("normal@example.com", "password123", roles=["employee"])
    access = login_user("normal@example.com", "password123").get_json()["access_token"]

    # Forbidden for non manager
    res = client.get("/analytics/attendance/summary", headers=auth_headers(access))
    assert res.status_code == 403


def test_analytics_endpoints_aggregate(client, register_user, login_user):
    _, mgr_token = setup_data_for_analytics(client, register_user, login_user)

    # Attendance summary
    res_att = client.get("/analytics/attendance/summary", headers=auth_headers(mgr_token))
    assert res_att.status_code == 200
    payload = res_att.get_json()
    assert payload["total_today"] >= 1
    assert "manual" in payload["by_method"]

    # Tasks status
    res_tasks = client.get("/analytics/tasks/status", headers=auth_headers(mgr_token))
    assert res_tasks.status_code == 200
    assert "by_status" in res_tasks.get_json()

    # Pending leaves
    res_leaves = client.get("/analytics/leaves/pending", headers=auth_headers(mgr_token))
    assert res_leaves.status_code == 200
    assert res_leaves.get_json()["pending"] >= 1

    # Unread notifications
    res_nt = client.get("/analytics/notifications/unread", headers=auth_headers(mgr_token))
    assert res_nt.status_code == 200
    assert res_nt.get_json()["unread"] >= 1
