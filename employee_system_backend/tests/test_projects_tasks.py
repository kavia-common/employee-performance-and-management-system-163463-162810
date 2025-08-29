from datetime import date
from .conftest import auth_headers

def test_projects_and_tasks_crud(client, register_user, login_user):
    register_user("pm@example.com", "password123", roles=["employee"])
    token = login_user("pm@example.com", "password123").get_json()["access_token"]

    # Projects
    res_list_p = client.get("/workitems/projects", headers=auth_headers(token))
    assert res_list_p.status_code == 200
    assert res_list_p.get_json() == []

    res_create_p = client.post("/workitems/projects", headers=auth_headers(token), json={
        "name": "Project A",
        "start_date": date.today().isoformat()
    })
    assert res_create_p.status_code == 201
    project = res_create_p.get_json()
    pid = project["id"]

    res_get_p = client.get(f"/workitems/projects/{pid}", headers=auth_headers(token))
    assert res_get_p.status_code == 200

    res_put_p = client.put(f"/workitems/projects/{pid}", headers=auth_headers(token), json={"description": "Desc"})
    assert res_put_p.status_code == 200
    assert res_put_p.get_json()["description"] == "Desc"

    # Tasks
    res_list_t = client.get("/workitems/tasks", headers=auth_headers(token))
    assert res_list_t.status_code == 200
    assert res_list_t.get_json() == []

    res_create_t = client.post("/workitems/tasks", headers=auth_headers(token), json={
        "project_id": pid,
        "title": "Task 1",
        "status": "todo",
        "priority": "high"
    })
    assert res_create_t.status_code == 201
    task = res_create_t.get_json()
    tid = task["id"]
    assert task["project_id"] == pid

    res_get_t = client.get(f"/workitems/tasks/{tid}", headers=auth_headers(token))
    assert res_get_t.status_code == 200

    res_put_t = client.put(f"/workitems/tasks/{tid}", headers=auth_headers(token), json={"status": "in_progress"})
    assert res_put_t.status_code == 200
    assert res_put_t.get_json()["status"] == "in_progress"

    # Delete task
    res_del_t = client.delete(f"/workitems/tasks/{tid}", headers=auth_headers(token))
    assert res_del_t.status_code == 200
    assert client.get(f"/workitems/tasks/{tid}", headers=auth_headers(token)).status_code == 404

    # Delete project
    res_del_p = client.delete(f"/workitems/projects/{pid}", headers=auth_headers(token))
    assert res_del_p.status_code == 200
    assert client.get(f"/workitems/projects/{pid}", headers=auth_headers(token)).status_code == 404
