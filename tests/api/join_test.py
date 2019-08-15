import pytest
from app.api.join import post
from app.models import TeamMember
from app.api.invite import encode
from tests.conftest import get_auth_token


def test_post_without_authtoken_fails(client):
    response = client.post("/api/join")
    assert response.status_code == 401


def test_post_with_authtoken_succeeds(client, team1):
    json = {"code": encode(team1)}
    headers = {"Authorization": get_auth_token(client)}
    response = client.post("/api/join", headers=headers, json=json)
    assert response.status_code == 200


def test_post_missing_attribute_fails(app, user1):
    with app.test_request_context(json={}):
        response = post(user1)
    assert response.status_code == 401
    assert "Missing key" in response.get_json()["message"]


def test_incorrect_code_fails(app, user1):
    with app.test_request_context(json={"code": "12345"}):
        response = post(user1)
    assert response.status_code == 401
    assert "Invalid code" in response.get_json()["message"]


def test_user_already_on_team_fails(app, user1, team1, team_member1):
    with app.test_request_context(json={"code": encode(team1)}):
        response = post(user1)
    assert response.status_code == 401
    assert "already a team member" in response.get_json()["message"]


def test_user_gets_added_to_team(app, session, user1, team1):
    with app.test_request_context(json={"code": encode(team1)}):
        post(user1)
    session.query(TeamMember).filter_by(user=user1, team=team1).one()


def test_response_contains_team_object(app, session, user1, team1):
    with app.test_request_context(json={"code": encode(team1)}):
        response = post(user1)

    session.add(team1)

    assert response.get_json() == team1.to_dict()
