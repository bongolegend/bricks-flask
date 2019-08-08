from tests.fixtures import client


def test_html_is_correct(client):
    result = client.get("/")
    assert b"Welcome" in result.data
