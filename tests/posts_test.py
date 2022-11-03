import pytest
from app import schemas


def test_get_all_posts(client, sample_posts):
    res = client.get("/posts/")
    assert res.status_code == 200
    posts = res.json()
    assert isinstance(posts, list)
    assert len(posts) == len(sample_posts)
    schemas.PostOut(**posts[0])


def test_get_one_post(client, sample_posts):
    local = sample_posts[0]
    res = client.get(f"/posts/{local.id}")
    assert res.status_code == 200
    foreign = schemas.PostOut(**res.json())
    assert local.title == foreign.Post.title


def test_create_post(authorized_client, test_user):
    post = {
        "title": "This is a Title", "content": "This is a sample content"
    }
    res = authorized_client.post("/posts/", json=post)
    assert res.status_code == 201
    new = schemas.Post(**res.json())
    assert new.user_id == test_user["id"]
    assert new.title == post["title"]


def test_create_post_unauthorized(client):
    post = {
        "title": "This is a Title", "content": "This is a sample content"
    }
    res = client.post("/posts/", json=post)
    assert res.status_code == 401


@pytest.mark.parametrize("title, content, status", [
    (None, "something", 422), ("somethin", None, 422), (None, None, 422)
])
def test_create_post_missing_required(authorized_client, title, content, status):
    res = authorized_client.post(
        "/posts/", json={"title": title, "content": content})
    assert res.status_code == status
