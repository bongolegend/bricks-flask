import pytest
from tests.conftest import get_auth_token
from app.api.feedback import post


def test_post_without_token_fails(client):
    response = client.post("/api/feedback")
    assert response.status_code == 401


def test_post_with_token_succeeds(client):
    json = {"text": "DUMMY MESSAGE"}
    headers = {"Authorization": get_auth_token(client)}
    response = client.post("/api/feedback", headers=headers, json=json)
    assert response.status_code == 200


def test_post_with_missing_attributes_fails(app, user1):
    with app.test_request_context(json={}):
        response = post(user1)
    assert response.status_code == 401
    assert "Missing key" in response.get_json()["message"]


# TODO need to test send_message
