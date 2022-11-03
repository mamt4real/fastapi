from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database import get_db, Base
import pytest
from app.oauth2 import create_access_token
from app import models

_exce = {1: "st", 2: 'nd', 3: "rd"}
_ranks = {
    x: _exce[x % 10] if x % 10 in _exce else "th" for x in range(1, 101)
}

SQLALCHEMY_DB_URL = f'postgresql://{settings.database_user}:{settings.database_pass}@{settings.database_host}:{settings.database_port}/{settings.database_name}_test'

engine = create_engine(SQLALCHEMY_DB_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    # run before tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture()
def test_user(client):
    data = {"email": "test@email.com", "password": "12345pass"}
    res = client.post("/users/", json=data)
    assert res.status_code == 201
    user = res.json()
    user["password"] = data["password"]
    return user


@pytest.fixture()
def test_user2(client):
    data = {"email": "test2@email.com", "password": "12345pass"}
    res = client.post("/users/", json=data)
    assert res.status_code == 201
    user = res.json()
    user["password"] = data["password"]
    return user


@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture
def sample_posts(test_user, test_user2, session):
    id = test_user["id"]
    posts = [{"title": f"{i}{_ranks[i]} title",
              "content": f"{i}{_ranks[i]} content", "user_id": id} for i in range(1, 6)]

    id = test_user2["id"]
    posts2 = [{"title": f"{i}{_ranks[i]} title",
              "content": f"{i}{_ranks[i]} content", "user_id": id} for i in range(6, 11)]

    session.add_all([models.Post(**post) for post in (*posts, *posts2)])
    session.commit()
    return session.query(models.Post).all()
