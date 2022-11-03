import pytest
from app import schemas
from jose import jwt
from app.config import settings


def test_create_user(client):
    res = client.post("/users/", json={
        "email": "sampleuser3@email.com", "password": "12345pass"
    })
    assert res.status_code == 201
    user = schemas.User(**res.json())
    assert user.email == "sampleuser3@email.com"


def test_login_user(test_user, client):
    res = client.post("/login", data={
        "username": test_user["email"], "password": test_user["password"]
    })
    assert res.status_code == 200
    tk = schemas.Token(**res.json())
    payload = jwt.decode(
        tk.access_token, settings.jwt_secret, settings.jwt_algorithm)
    id = payload.get("user_id")
    assert id == test_user["id"]
    assert tk.token_type == "bearer"


@pytest.mark.parametrize("email, password, s_code", [
    ("wrong_email@gmail.com", "12345pass", 401),
    ("testl@email.com", "wrong_pass", 401),
    ("wrong_email@gmail.com", "wrong_pass", 401),
    (None, "12345pass", 422),
    ("testl@email.com", None, 422),
])
def test_incorrect_login(client, email, password, s_code):
    res = client.post("/login", data={
        "username": email, "password": password
    })
    assert res.status_code == s_code
