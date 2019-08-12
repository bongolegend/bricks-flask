import pytest
from tests.conftest import get_auth_token
from app.api.app_user import put
from app.models import AppUser


def test_api_without_authtoken(client):
    response = client.put("/api/app_user")
    assert response.status_code == 401


def test_api_with_authtoken(client):
    headers = {"Authorization": get_auth_token(client)}
    response = client.put("/api/app_user", headers=headers, json={})
    assert response.status_code == 200


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


def test_updated_user_saved_to_db(app, session):
    user = AppUser(username="mia")
    session.add(user)
    session.commit()

    json = {"username": "bob"}
    with app.test_request_context(json=json):
        put(user)

    session.add(user)
    updated_user = session.query(AppUser).filter_by(id=user.id).one()
    assert updated_user.username == "bob"
