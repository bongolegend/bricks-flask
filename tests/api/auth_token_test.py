from tests.conftest import client, db
from app.models import AppUser

MOCK_TOKEN = "MOCK_TOKEN"
FIR_AUTH_ID = "FIR_AUTH_ID"


def test_firtoken_is_missing(client):
    response = client.get("/api/auth_token")
    assert response.status_code == 401
    assert "Authorization" in response.get_json()["message"]


def test_firtoken_is_incorrect(client):
    headers = {"Authorization": "BAD_MOCK_TOKEN"}
    response = client.get("/api/auth_token", headers=headers)
    assert response.status_code == 401
    assert "not accepted" in response.get_json()["message"]


def test_firtoken_is_correct_for_new_user(client):
    headers = {"Authorization": MOCK_TOKEN}
    response = client.get("/api/auth_token", headers=headers)
    data = response.get_json()
    assert response.status_code == 202
    assert len(data["auth_token"]) > 10 and isinstance(data["auth_token"], str)
    assert data["user_id"] == 1
    assert data["duration"] == 86400


def test_firtoken_is_correct_for_existing_user(client, db):
    existing_user = AppUser(id=123, fir_auth_id=FIR_AUTH_ID)
    db.session.add(existing_user)
    headers = {"Authorization": MOCK_TOKEN}
    response = client.get("/api/auth_token", headers=headers)
    assert response.status_code == 202
    assert response.get_json()["user_id"] == 123
