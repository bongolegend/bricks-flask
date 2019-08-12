import pytest
from tests.conftest import get_auth_token


def test_post_without_authtoken_fails(client):
    response = client.post("/api/assist")
    assert response.status_code == 401


def test_post_with_authtoken_succeeds(client, team_member1):
    json = {"action": "NUDGE", "assistee_member_id": team_member1.id}
    headers = {"Authorization": get_auth_token(client)}
    response = client.post("/api/assist", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.xfail()
def test_post_request_missing_an_attribute_fails():
    assert 0


@pytest.mark.xfail()
def test_assist_added_to_db():
    assert 0
