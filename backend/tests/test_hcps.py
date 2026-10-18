def test_hcps_require_login(client):
    response = client.get("/api/hcps")
    assert response.status_code in (401, 403)


def test_list_hcps(client, auth_headers, make_hcp):
    headers = auth_headers()
    make_hcp(full_name="Dr. Alpha")
    make_hcp(full_name="Dr. Beta")
    response = client.get("/api/hcps", headers=headers)
    assert response.status_code == 200
    names = [h["full_name"] for h in response.json()]
    assert names == ["Dr. Alpha", "Dr. Beta"]


def test_search_by_name_is_case_insensitive(client, auth_headers, make_hcp):
    headers = auth_headers()
    make_hcp(full_name="Dr. Rohan Kapoor")
    make_hcp(full_name="Dr. Sneha Iyer")
    response = client.get("/api/hcps", params={"q": "rohan"}, headers=headers)
    assert [h["full_name"] for h in response.json()] == ["Dr. Rohan Kapoor"]


def test_search_by_specialty(client, auth_headers, make_hcp):
    headers = auth_headers()
    make_hcp(full_name="Dr. A", specialty="Cardiology")
    make_hcp(full_name="Dr. B", specialty="Oncology")
    response = client.get("/api/hcps", params={"q": "cardio"}, headers=headers)
    assert [h["full_name"] for h in response.json()] == ["Dr. A"]


def test_search_no_match_returns_empty_list(client, auth_headers, make_hcp):
    headers = auth_headers()
    make_hcp(full_name="Dr. A")
    response = client.get("/api/hcps", params={"q": "zzz"}, headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_hcp_by_id(client, auth_headers, make_hcp):
    headers = auth_headers()
    hcp = make_hcp(full_name="Dr. Single")
    response = client.get(f"/api/hcps/{hcp.id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Dr. Single"


def test_get_hcp_not_found(client, auth_headers):
    headers = auth_headers()
    response = client.get("/api/hcps/999", headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "HCP not found"