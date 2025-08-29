from datetime import date, timedelta
from .conftest import auth_headers

def test_leaves_flow_with_approvals(client, register_user, login_user):
    # Requester is employee, approver is manager
    register_user("emp2@example.com", "password123", roles=["employee"])
    register_user("mgr@example.com", "password123", roles=["manager"])

    emp_token = login_user("emp2@example.com", "password123").get_json()["access_token"]
    mgr_token = login_user("mgr@example.com", "password123").get_json()["access_token"]

    # Employee creates leave
    start = date.today()
    end = start + timedelta(days=2)
    res_create = client.post("/leaves/", headers=auth_headers(emp_token), json={
        "user_id": 1,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "type": "vacation",
        "reason": "Family"
    })
    assert res_create.status_code == 201
    leave = res_create.get_json()
    lid = leave["id"]
    assert leave["status"] == "pending"

    # Employee can view
    res_get = client.get(f"/leaves/{lid}", headers=auth_headers(emp_token))
    assert res_get.status_code == 200

    # Employee can update while pending
    res_put = client.put(f"/leaves/{lid}", headers=auth_headers(emp_token), json={"reason": "Family trip"})
    assert res_put.status_code == 200
    assert res_put.get_json()["reason"] == "Family trip"

    # Manager approves
    res_appr = client.post(f"/leaves/{lid}/approve", headers=auth_headers(mgr_token))
    assert res_appr.status_code == 200
    assert res_appr.get_json()["status"] == "approved"

    # After approve, employee cannot update
    res_put_block = client.put(f"/leaves/{lid}", headers=auth_headers(emp_token), json={"reason": "Changed"})
    assert res_put_block.status_code == 400

    # New pending leave to test rejection
    res_create2 = client.post("/leaves/", headers=auth_headers(emp_token), json={
        "user_id": 1,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "type": "sick",
    })
    lid2 = res_create2.get_json()["id"]
    res_rej = client.post(f"/leaves/{lid2}/reject", headers=auth_headers(mgr_token))
    assert res_rej.status_code == 200
    assert res_rej.get_json()["status"] == "rejected"

    # Employee can cancel a pending request
    res_create3 = client.post("/leaves/", headers=auth_headers(emp_token), json={
        "user_id": 1,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "type": "personal",
    })
    lid3 = res_create3.get_json()["id"]
    res_cancel = client.delete(f"/leaves/{lid3}", headers=auth_headers(emp_token))
    assert res_cancel.status_code == 200
