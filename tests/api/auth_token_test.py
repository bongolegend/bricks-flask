from tests.fixtures import client


def test_firtoken_is_missing(client):
    result = client.get("/api/auth_token")
    assert result.status_code == 401
