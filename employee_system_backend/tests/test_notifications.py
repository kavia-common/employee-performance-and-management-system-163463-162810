from .conftest import auth_headers

def test_notifications_create_and_read(client, register_user, login_user):
    # Manager creates notifications for employee
    register_user("emp3@example.com", "password123", roles=["employee"])
    register_user("mgr2@example.com", "password123", roles=["manager"])

    emp_login = login_user("emp3@example.com", "password123").get_json()
    emp_id = emp_login["user"]["id"]
    emp_token = emp_login["access_token"]
    mgr_token = login_user("mgr2@example.com", "password123").get_json()["access_token"]

    # Employee list empty
    res_list_empty = client.get("/notifications/", headers=auth_headers(emp_token))
    assert res_list_empty.status_code == 200
    assert res_list_empty.get_json() == []

    # Employee cannot create
    res_create_forbidden = client.post("/notifications/", headers=auth_headers(emp_token), json={
        "user_id": emp_id, "title": "Hi", "message": "Welcome"
    })
    assert res_create_forbidden.status_code == 403

    # Manager can create
    res_create = client.post("/notifications/", headers=auth_headers(mgr_token), json={
        "user_id": emp_id, "title": "Reminder", "message": "Submit report", "level": "warning"
    })
    assert res_create.status_code == 201
    note = res_create.get_json()
    nid = note["id"]
    assert note["level"] == "warning"

    # Employee sees it
    res_list = client.get("/notifications/", headers=auth_headers(emp_token))
    assert res_list.status_code == 200
    assert len(res_list.get_json()) == 1

    # Mark as read
    res_read = client.post(f"/notifications/{nid}/read", headers=auth_headers(emp_token))
    assert res_read.status_code == 200
    assert res_read.get_json()["is_read"] is True
