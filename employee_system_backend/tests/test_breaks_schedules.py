from datetime import datetime, time, timezone
from .conftest import auth_headers

def test_breaks_crud(client, register_user, login_user):
    register_user("br@example.com", "password123", roles=["employee"])
    access = login_user("br@example.com", "password123").get_json()["access_token"]

    # No breaks initially
    res_list = client.get("/work/breaks", headers=auth_headers(access))
    assert res_list.status_code == 200
    assert res_list.get_json() == []

    # Create break
    start = datetime.now(timezone.utc).isoformat()
    res_create = client.post("/work/breaks", headers=auth_headers(access), json={
        "user_id": 1,
        "start_time": start,
        "type": "lunch"
    })
    assert res_create.status_code == 201
    br = res_create.get_json()
    br_id = br["id"]
    assert br["type"] == "lunch"

    # Update break
    res_put = client.put(f"/work/breaks/{br_id}", headers=auth_headers(access), json={"type": "personal"})
    assert res_put.status_code == 200
    assert res_put.get_json()["type"] == "personal"

    # Delete break
    res_del = client.delete(f"/work/breaks/{br_id}", headers=auth_headers(access))
    assert res_del.status_code == 200

    # Not found after delete
    res_put_404 = client.put(f"/work/breaks/{br_id}", headers=auth_headers(access), json={"type": "break"})
    assert res_put_404.status_code == 404


def test_schedules_crud(client, register_user, login_user):
    register_user("sc@example.com", "password123", roles=["employee"])
    access = login_user("sc@example.com", "password123").get_json()["access_token"]

    # List empty
    res_list = client.get("/work/schedules", headers=auth_headers(access))
    assert res_list.status_code == 200
    assert res_list.get_json() == []

    # Create
    res_create = client.post("/work/schedules", headers=auth_headers(access), json={
        "user_id": 1,
        "day_of_week": 1,
        "start_time": time(9,0).isoformat(),
        "end_time": time(17,0).isoformat(),
    })
    assert res_create.status_code == 201
    sc = res_create.get_json()
    sc_id = sc["id"]

    # Update
    res_put = client.put(f"/work/schedules/{sc_id}", headers=auth_headers(access), json={"day_of_week": 2})
    assert res_put.status_code == 200
    assert res_put.get_json()["day_of_week"] == 2

    # Delete
    res_del = client.delete(f"/work/schedules/{sc_id}", headers=auth_headers(access))
    assert res_del.status_code == 200

    # Not found after delete
    res_put_404 = client.put(f"/work/schedules/{sc_id}", headers=auth_headers(access), json={"day_of_week": 3})
    assert res_put_404.status_code == 404
