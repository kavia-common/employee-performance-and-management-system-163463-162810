from datetime import datetime, timedelta, timezone
from .conftest import auth_headers

def test_meetings_flow(client, register_user, login_user, session):
    # Organizer and another user
    register_user("org@example.com", "password123", roles=["employee"])
    register_user("usr@example.com", "password123", roles=["employee"])

    org_token = login_user("org@example.com", "password123").get_json()["access_token"]
    usr_token = login_user("usr@example.com", "password123").get_json()["access_token"]

    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=1)

    # Organizer creates meeting
    res_create = client.post("/meetings/", headers=auth_headers(org_token), json={
        "organizer_id": 1,
        "title": "Sprint Planning",
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "is_virtual": True
    })
    assert res_create.status_code == 201
    meeting = res_create.get_json()
    mid = meeting["id"]

    # Organizer can get it
    res_get = client.get(f"/meetings/{mid}", headers=auth_headers(org_token))
    assert res_get.status_code == 200

    # Non-participant cannot get until added
    res_get_usr = client.get(f"/meetings/{mid}", headers=auth_headers(usr_token))
    assert res_get_usr.status_code == 404

    # Add user as participant
    # fetch usr id (second registered user will have id 2 under isolated session)
    res_add = client.post(f"/meetings/{mid}/participants", headers=auth_headers(org_token), json={
        "meeting_id": mid,
        "user_id": 2
    })
    assert res_add.status_code in (200, 201)

    # Now user can get meeting
    res_get_usr2 = client.get(f"/meetings/{mid}", headers=auth_headers(usr_token))
    assert res_get_usr2.status_code == 200

    # List meetings for participant
    res_list_usr = client.get("/meetings/", headers=auth_headers(usr_token))
    assert res_list_usr.status_code == 200
    assert any(m["id"] == mid for m in res_list_usr.get_json())

    # Update meeting by organizer
    res_put = client.put(f"/meetings/{mid}", headers=auth_headers(org_token), json={"title": "Sprint Planning v2"})
    assert res_put.status_code == 200
    assert res_put.get_json()["title"] == "Sprint Planning v2"

    # Delete meeting by organizer
    res_del = client.delete(f"/meetings/{mid}", headers=auth_headers(org_token))
    assert res_del.status_code == 200

    # Not found after delete
    res_get_deleted = client.get(f"/meetings/{mid}", headers=auth_headers(org_token))
    assert res_get_deleted.status_code == 404
