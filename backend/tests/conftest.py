import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app
from app.models import HCP, FollowUp, Interaction, Product, User  # noqa: F401
from app.core.security import hash_password

TEST_DB_NAME = "crm_hcp_test"

test_url = make_url(settings.database_url).set(database=TEST_DB_NAME)
# Safety guard: never run tests against a database that isn't clearly a test one.
assert test_url.database is not None and test_url.database.endswith("_test")

engine = create_engine(test_url, pool_pre_ping=True)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def create_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    names = ", ".join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {names} RESTART IDENTITY CASCADE"))


@pytest.fixture()
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()



TEST_PASSWORD = "Test@1234"


@pytest.fixture()
def make_user(db):
    def _make_user(email="rep@test.com", full_name="Test Rep", is_active=True):
        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(TEST_PASSWORD),
            territory="Test Territory",
            is_active=is_active,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return _make_user


@pytest.fixture()
def make_hcp(db):
    def _make_hcp(full_name="Dr. Test", specialty="Cardiology", city="Mumbai"):
        hcp = HCP(full_name=full_name, specialty=specialty, city=city)
        db.add(hcp)
        db.commit()
        db.refresh(hcp)
        return hcp

    return _make_hcp


@pytest.fixture()
def make_product(db):
    def _make_product(name="TestProduct"):
        product = Product(name=name, category="Test")
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    return _make_product


@pytest.fixture()
def auth_headers(client, make_user):
    def _auth_headers(email="rep@test.com"):
        make_user(email=email)
        response = client.post(
            "/api/auth/login", json={"email": email, "password": TEST_PASSWORD}
        )
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers