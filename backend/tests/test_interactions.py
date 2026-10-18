BASE_PAYLOAD = {
    "interaction_type": "visit",
    "interaction_date": "2026-10-12T10:00:00Z",
}


def make_payload(hcp_id, **overrides):
    return {**BASE_PAYLOAD, "hcp_id": hcp_id, **overrides}


def test_interactions_require_login(client):
    assert client.get("/api/interactions").status_code in (401, 403)
    assert client.post("/api/interactions", json={}).status_code in (401, 403)


def test_create_interaction_with_products_and_followups(
    client, auth_headers, make_hcp, make_product
):
    headers = auth_headers()
    hcp = make_hcp(full_name="Dr. Kapoor")
    product = make_product("CardioSafe")
    payload = make_payload(
        hcp.id,
        sentiment="positive",
        summary="Discussed dosing.",
        product_ids=[product.id],
        follow_ups=[{"description": "Send PDF", "due_date": "2026-10-16"}],
    )
    response = client.post("/api/interactions", json=payload, headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["hcp"]["full_name"] == "Dr. Kapoor"
    assert body["sentiment"] == "positive"
    assert body["source"] == "form"
    assert [p["name"] for p in body["products"]] == ["CardioSafe"]
    assert len(body["follow_ups"]) == 1
    assert body["follow_ups"][0]["status"] == "pending"


def test_create_rejects_invalid_type(client, auth_headers, make_hcp):
    headers = auth_headers()
    hcp = make_hcp()
    payload = make_payload(hcp.id, interaction_type="dance")
    response = client.post("/api/interactions", json=payload, headers=headers)
    assert response.status_code == 422


def test_create_rejects_invalid_sentiment(client, auth_headers, make_hcp):
    headers = auth_headers()
    hcp = make_hcp()
    payload = make_payload(hcp.id, sentiment="ecstatic")
    response = client.post("/api/interactions", json=payload, headers=headers)
    assert response.status_code == 422


def test_create_rejects_unknown_field(client, auth_headers, make_hcp):
    headers = auth_headers()
    hcp = make_hcp()
    payload = make_payload(hcp.id, invented_field="x")
    response = client.post("/api/interactions", json=payload, headers=headers)
    assert response.status_code == 422


def test_create_unknown_hcp_returns_404(client, auth_headers):
    headers = auth_headers()
    response = client.post("/api/interactions", json=make_payload(999), headers=headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "HCP not found"


def test_create_unknown_product_returns_400(client, auth_headers, make_hcp):
    headers = auth_headers()
    hcp = make_hcp()
    payload = make_payload(hcp.id, product_ids=[999])
    response = client.post("/api/interactions", json=payload, headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "One or more products do not exist"


def test_list_filters_by_hcp(client, auth_headers, make_hcp):
    headers = auth_headers()
    hcp_a = make_hcp(full_name="Dr. A")
    hcp_b = make_hcp(full_name="Dr. B")
    client.post("/api/interactions", json=make_payload(hcp_a.id), headers=headers)
    client.post("/api/interactions", json=make_payload(hcp_b.id), headers=headers)

    all_rows = client.get("/api/interactions", headers=headers).json()
    only_a = client.get(
        "/api/interactions", params={"hcp_id": hcp_a.id}, headers=headers
    ).json()
    assert len(all_rows) == 2
    assert len(only_a) == 1
    assert only_a[0]["hcp"]["full_name"] == "Dr. A"


def test_partial_edit_changes_only_sent_fields(client, auth_headers, make_hcp):
    headers = auth_headers()
    hcp = make_hcp()
    created = client.post(
        "/api/interactions",
        json=make_payload(hcp.id, sentiment="positive", summary="Original summary"),
        headers=headers,
    ).json()

    response = client.patch(
        f"/api/interactions/{created['id']}",
        json={"sentiment": "negative"},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sentiment"] == "negative"
    assert body["summary"] == "Original summary"
    assert body["interaction_type"] == "visit"


def test_edit_replaces_products(client, auth_headers, make_hcp, make_product):
    headers = auth_headers()
    hcp = make_hcp()
    first = make_product("First")
    second = make_product("Second")
    created = client.post(
        "/api/interactions",
        json=make_payload(hcp.id, product_ids=[first.id]),
        headers=headers,
    ).json()

    response = client.patch(
        f"/api/interactions/{created['id']}",
        json={"product_ids": [second.id]},
        headers=headers,
    )
    assert [p["name"] for p in response.json()["products"]] == ["Second"]


def test_edit_rejects_invalid_value(client, auth_headers, make_hcp):
    headers = auth_headers()
    hcp = make_hcp()
    created = client.post(
        "/api/interactions", json=make_payload(hcp.id), headers=headers
    ).json()
    response = client.patch(
        f"/api/interactions/{created['id']}",
        json={"sentiment": "ecstatic"},
        headers=headers,
    )
    assert response.status_code == 422


def test_edit_cannot_change_hcp(client, auth_headers, make_hcp):
    headers = auth_headers()
    hcp = make_hcp()
    other = make_hcp(full_name="Dr. Other")
    created = client.post(
        "/api/interactions", json=make_payload(hcp.id), headers=headers
    ).json()
    response = client.patch(
        f"/api/interactions/{created['id']}",
        json={"hcp_id": other.id},
        headers=headers,
    )
    assert response.status_code == 422


def test_rep_cannot_see_or_edit_another_reps_interaction(
    client, auth_headers, make_hcp
):
    headers_a = auth_headers("a@test.com")
    headers_b = auth_headers("b@test.com")
    hcp = make_hcp()
    created = client.post(
        "/api/interactions", json=make_payload(hcp.id), headers=headers_a
    ).json()
    interaction_id = created["id"]

    assert client.get(f"/api/interactions/{interaction_id}", headers=headers_b).status_code == 404
    assert (
        client.patch(
            f"/api/interactions/{interaction_id}",
            json={"sentiment": "negative"},
            headers=headers_b,
        ).status_code
        == 404
    )
    assert client.get("/api/interactions", headers=headers_b).json() == []
    # the owner still sees it
    assert client.get(f"/api/interactions/{interaction_id}", headers=headers_a).status_code == 200