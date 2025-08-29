def test_health_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.get_json()
    assert data["message"] == "Healthy"
