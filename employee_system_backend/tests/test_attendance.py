from datetime import datetime, timezone
from .conftest import auth_headers

def test_attendance_crud_and_checkout(client, register_user, login_user):
    register_user("att@example.com", "password123", roles=["employee"])
    access = login_user("att@example.com", "password123").get_json()["access_token"]

    # Initially empty list
    res_list_empty = client.get("/attendance/", headers=auth_headers(access))
    assert res_list_empty.status_code == 200
    assert res_list_empty.get_json() == []

    # Create invalid method
    bad = client.post("/attendance/", headers=auth_headers(access), json={
        "user_id": 1, "method": "unknown"
    })
    assert bad.status_code == 400

    # Create valid manual record
    now = datetime.now(timezone.utc).isoformat()
    res_create = client.post("/attendance/", headers=auth_headers(access), json={
        "user_id": 1,
        "method": "manual",
        "check_in_time": now,
        "notes": "On time",
    })
    assert res_create.status_code == 201
    att = res_create.get_json()
    assert att["method"] == "manual"
    att_id = att["id"]

    # List contains the record
    res_list = client.get("/attendance/", headers=auth_headers(access))
    assert res_list.status_code == 200
    assert len(res_list.get_json()) == 1

    # Checkout
    res_checkout = client.post(f"/attendance/{att_id}/checkout", headers=auth_headers(access))
    assert res_checkout.status_code == 200
    assert res_checkout.get_json()["check_out_time"] is not None

    # Checkout again should fail
    res_checkout_again = client.post(f"/attendance/{att_id}/checkout", headers=auth_headers(access))
    assert res_checkout_again.status_code == 400
