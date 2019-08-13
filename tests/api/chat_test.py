import pytest
from tests.conftest import get_auth_token
from app.api.chat import post, get_team_members
from app.models import AppUser, TeamMember
from app.constants import Statuses


def test_post_without_authtoken_fails(client):
    response = client.post("/api/chat")
    assert response.status_code == 401


def test_post_with_authtoken_succeeds(client, team1):
    json = {"team_id": team1.id, "content": ""}
    headers = {"Authorization": get_auth_token(client)}
    response = client.post("api/chat", headers=headers, json=json)
    assert response.status_code == 200


@pytest.mark.parametrize("json", [{"team_id": 1}, {"content": "DUMMY MESSAGE"}])
def test_post_missing_attributes_fails(app, user1, json):
    with pytest.raises(KeyError):
        with app.test_request_context(json=json):
            post(user1)


def test_module_filters_team_members_correctly(app, session, team1, user1):
    jim = AppUser(username="jim", chat_notifs=False)
    bill = AppUser(username="bill", chat_notifs=True, fir_push_notif_token="FAKE TOKEN")
    session.add(jim)
    session.add(bill)

    jim_member = TeamMember(user=jim, team=team1, inviter=user1, status=Statuses.ACTIVE)
    bill_member = TeamMember(
        user=bill, team=team1, inviter=user1, status=Statuses.ACTIVE
    )
    session.add(jim_member)
    session.add(bill_member)

    session.commit()
    filtered_members = get_team_members(team1.id, user1.id)
    expected_members = [bill]
    assert expected_members == filtered_members


@pytest.mark.xfail()
def test_post_with_nonexistent_team_id_fails():
    assert 0


# I need to write tests else-where to make sure the notifications get sent
