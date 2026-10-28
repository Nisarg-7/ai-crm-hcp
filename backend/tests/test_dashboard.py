from datetime import datetime, timedelta, timezone


def iso_days_ago(days):
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()


def log(client, headers, hcp_id, days_ago=0, follow_ups=None):
    payload = {
        "hcp_id": hcp_id,
        "interaction_type": "visit",
        "interaction_date": iso_days_ago(days_ago),
        "follow_ups": follow_ups or [],
    }
    response = client.post("/api/interactions", json=payload, headers=headers)
    assert response.status_code == 201
    return response.json()


def test_dashboard_requires_login(client):
    assert client.get("/api/dashboard").status_code in (401, 403)


def test_dashboard_empty(client, auth_headers):
    headers = auth_headers()
    body = client.get("/api/dashboard", headers=headers).json()
    assert body["counts"] == {
        "total_interactions": 0,
        "last_7_days": 0,
        "open_follow_ups": 0,
    }
    assert body["recent_interactions"] == []
    assert body["open_follow_ups"] == []


def test_dashboard_counts_and_lists(client, auth_headers, make_hcp):
    headers = auth_headers()
    hcp = make_hcp(full_name="Dr. Dash")
    log(client, headers, hcp.id, days_ago=1, follow_ups=[
        {"description": "Later", "due_date": "2026-12-01"},
        {"description": "Sooner", "due_date": "2026-11-01"},
        {"description": "No date"},
    ])
    log(client, headers, hcp.id, days_ago=30)

    body = client.get("/api/dashboard", headers=headers).json()
    assert body["counts"]["total_interactions"] == 2
    assert body["counts"]["last_7_days"] == 1
    assert body["counts"]["open_follow_ups"] == 3
    assert body["recent_interactions"][0]["hcp_name"] == "Dr. Dash"
    descriptions = [f["description"] for f in body["open_follow_ups"]]
    assert descriptions == ["Sooner", "Later", "No date"]


def test_dashboard_only_shows_own_data(client, auth_headers, make_hcp):
    headers_a = auth_headers("a@test.com")
    headers_b = auth_headers("b@test.com")
    hcp = make_hcp()
    log(client, headers_a, hcp.id, follow_ups=[{"description": "Mine"}])

    body = client.get("/api/dashboard", headers=headers_b).json()
    assert body["counts"]["total_interactions"] == 0
    assert body["open_follow_ups"] == []