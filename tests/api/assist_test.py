import pytest
from tests.conftest import get_auth_token
from app.api.assist import post
from app.models import Assist


def test_post_without_authtoken_fails(client):
    response = client.post("/api/assist")
    assert response.status_code == 401


def test_post_with_authtoken_succeeds(client, team_member1):
    json = {"action": "NUDGE", "assistee_member_id": team_member1.id}
    headers = {"Authorization": get_auth_token(client)}
    response = client.post("/api/assist", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "attribute,value", [("action", "NUDGE"), ("assistee_member_id", 1)]
)
def test_post_fails_if_request_missing_an_attribute(
    app, user1, team_member1, attribute, value
):
    json = {attribute: value}
    with app.test_request_context(json=json):
        response = post(user1)
    assert response.status_code == 401


def test_assist_added_to_db(app, session, user1, team_member1):
    json = {"action": "UNIQUE_ACTION", "assistee_member_id": team_member1.id}
    with app.test_request_context(json=json):
        post(user1)
    session.query(Assist).filter_by(action="UNIQUE_ACTION").one()
