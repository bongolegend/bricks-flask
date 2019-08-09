import pytest
from app import create_app, db


@pytest.fixture
def client():
    app = create_app(test=True)
    client = app.test_client()

    yield client


@pytest.fixture
def app():
    app = create_app(test=True)
    yield app
