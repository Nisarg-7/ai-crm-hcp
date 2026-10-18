from tests.conftest import TEST_PASSWORD


def test_login_success(client, make_user):
    make_user(email="a@test.com")
    response = client.post(
        "/api/auth/login", json={"email": "a@test.com", "password": TEST_PASSWORD}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "a@test.com"
    assert "hashed_password" not in body["user"]


def test_login_wrong_password(client, make_user):
    make_user(email="a@test.com")
    response = client.post(
        "/api/auth/login", json={"email": "a@test.com", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_unknown_email_gives_same_message(client):
    response = client.post(
        "/api/auth/login", json={"email": "nobody@test.com", "password": "x"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_inactive_user_rejected(client, make_user):
    make_user(email="off@test.com", is_active=False)
    response = client.post(
        "/api/auth/login", json={"email": "off@test.com", "password": TEST_PASSWORD}
    )
    assert response.status_code == 401


def test_login_invalid_email_format(client):
    response = client.post(
        "/api/auth/login", json={"email": "not-an-email", "password": "x"}
    )
    assert response.status_code == 422


def test_me_with_valid_token(client, auth_headers):
    headers = auth_headers("me@test.com")
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "me@test.com"


def test_me_without_token_is_blocked(client):
    response = client.get("/api/auth/me")
    assert response.status_code in (401, 403)


def test_me_with_bad_token(client):
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer abc"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"