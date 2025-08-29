from .conftest import auth_headers

def test_roles_rbac_requires_super_admin(client, register_user, login_user):
    # regular employee
    register_user("emp@example.com", "password123", roles=["employee"])
    emp_login = login_user("emp@example.com", "password123").get_json()
    emp_access = emp_login["access_token"]

    # super admin
    register_user("admin@example.com", "password123", roles=["super_admin"])
    admin_access = login_user("admin@example.com", "password123").get_json()["access_token"]

    # Employee cannot access list
    res_list = client.get("/roles/", headers=auth_headers(emp_access))
    assert res_list.status_code == 403

    # Super admin can list (initial seeded roles present)
    res_list_admin = client.get("/roles/", headers=auth_headers(admin_access))
    assert res_list_admin.status_code == 200
    roles = res_list_admin.get_json()
    assert any(r["name"] == "super_admin" for r in roles)

    # Employee cannot create
    res_create = client.post("/roles/", headers=auth_headers(emp_access), json={"name": "auditor"})
    assert res_create.status_code == 403

    # Super admin creates role
    res_create_admin = client.post("/roles/", headers=auth_headers(admin_access), json={"name": "auditor"})
    assert res_create_admin.status_code == 201
    role_id = res_create_admin.get_json()["id"]

    # Duplicate role blocked
    res_dup = client.post("/roles/", headers=auth_headers(admin_access), json={"name": "auditor"})
    assert res_dup.status_code == 409

    # Fetch role
    res_get = client.get(f"/roles/{role_id}", headers=auth_headers(admin_access))
    assert res_get.status_code == 200
    assert res_get.get_json()["name"] == "auditor"

    # Update role
    res_put = client.put(f"/roles/{role_id}", headers=auth_headers(admin_access), json={"description": "Audits stuff"})
    assert res_put.status_code == 200
    assert res_put.get_json()["description"] == "Audits stuff"

    # Delete role
    res_del = client.delete(f"/roles/{role_id}", headers=auth_headers(admin_access))
    assert res_del.status_code == 200

    # Deleted role not retrievable
    res_get_deleted = client.get(f"/roles/{role_id}", headers=auth_headers(admin_access))
    assert res_get_deleted.status_code == 404
