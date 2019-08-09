import pytest
from tests.fixtures import client, app
from app.api.app_user import put
from app.models import AppUser


def test_api_without_authtoken(client):
    response = client.put("/api/app_user")
    assert response.status_code == 401


@pytest.mark.xfail()
def test_api_with_authtoken(client):
    assert False


@pytest.mark.parametrize(
    "user,json,attribute",
    [
        (AppUser(device_token="456"), {"device_token": "123"}, "device_token"),
        (AppUser(username="jo"), {"username": "jimmy"}, "username"),
        (
            AppUser(fir_push_notif_token="456"),
            {"fir_push_notif_token": "123"},
            "fir_push_notif_token",
        ),
        (AppUser(fir_auth_id="456"), {"fir_auth_id": "123"}, "fir_auth_id"),
        (AppUser(email="a@b.com"), {"email": "x@y.com"}, "email"),
        (AppUser(chat_notifs=True), {"chat_notifs": False}, "chat_notifs"),
        (AppUser(task_notifs=True), {"task_notifs": False}, "task_notifs"),
    ],
)
def test_response_contains_updated_user(app, user, json, attribute):
    with app.test_request_context(json=json):
        response = put(user)
        assert response.get_json()[attribute] == json[attribute]


@pytest.mark.xfail()
def test_updated_user_saved_to_db():
    assert False
