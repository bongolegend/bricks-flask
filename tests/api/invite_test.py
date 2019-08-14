import pytest
import os
from tests.conftest import get_auth_token
from app.api.invite import post
from app.models import Invitation


def test_post_without_authtoken_fails(client):
    response = client.post("/api/invite")
    assert response.status_code == 401


def test_post_with_authtoken_succeeds(client, team1):
    json = {"team_id": team1.id, "phone_number": os.environ.get("NICO_PHONE_NUMBER")}
    headers = {"Authorization": get_auth_token(client)}
    response = client.post("api/invite", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "json", [{"team_id": 1}, {"phone_number": os.environ.get("NICO_PHONE_NUMBER")}]
)
def test_post_missing_attributes_fails(app, user1, json):
    with app.test_request_context(json=json):
        response = post(user1)
    assert response.status_code == 401
    assert "Missing key" in response.get_json()["message"]


def test_bad_phone_number_fails(app, user1, team1):
    with app.test_request_context(json={"team_id": team1.id, "phone_number": "123"}):
        response = post(user1)
    assert response.status_code == 401
    assert "Invalid phone number" in response.get_json()["message"]


def test_post_with_nonexistent_team_id_fails(app, user1):
    json = {"team_id": 999, "phone_number": os.environ.get("NICO_PHONE_NUMBER")}
    with app.test_request_context(json=json):
        response = post(user1)
    assert response.status_code == 401


def test_invitation_gets_added_to_db(app, session, team1, user1):
    pre_count = session.query(Invitation).count()

    json = {"team_id": team1.id, "phone_number": os.environ.get("NICO_PHONE_NUMBER")}
    with app.test_request_context(json=json):
        post(user1)

    post_count = session.query(Invitation).count()
    assert pre_count + 1 == post_count


# TODO test the send_message api
