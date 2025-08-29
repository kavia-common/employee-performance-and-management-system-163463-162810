from .conftest import auth_headers

def test_register_and_login_flow(client, register_user, login_user):
    # Register
    r = register_user("user1@example.com", "password123", first_name="U", last_name="One", roles=["employee"])
    assert r.status_code == 201
    user = r.get_json()
    assert user["email"] == "user1@example.com"

    # Duplicate registration
    r_dup = register_user("user1@example.com", "password123")
    assert r_dup.status_code == 409

    # Login success
    l = login_user("user1@example.com", "password123")
    assert l.status_code == 200
    payload = l.get_json()
    assert "access_token" in payload and "refresh_token" in payload
    assert payload["user"]["email"] == "user1@example.com"

    # Login failure
    l_bad = login_user("user1@example.com", "wrong")
    assert l_bad.status_code == 401


def test_refresh_and_me_endpoint(client, register_user, login_user):
    # Prepare a registered user with role employee
    r = register_user("user2@example.com", "password123", roles=["employee"])
    assert r.status_code == 201

    login = login_user("user2@example.com", "password123").get_json()
    access = login["access_token"]
    refresh = login["refresh_token"]

    # /auth/me with access token
    me_res = client.get("/auth/me", headers=auth_headers(access))
    assert me_res.status_code == 200
    me = me_res.get_json()
    assert me["email"] == "user2@example.com"

    # /auth/refresh using refresh token
    ref_res = client.post("/auth/refresh", headers={"Authorization": f"Bearer {refresh}"})
    assert ref_res.status_code == 200
    refreshed = ref_res.get_json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"] is None
    assert refreshed["user"]["email"] == "user2@example.com"
