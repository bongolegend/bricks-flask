import pytest
from app import create_app, db as _db


@pytest.fixture
def app():
    app = create_app(test=True)
    return app


@pytest.fixture
def db(app):
    _db.app = app
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture
def client(app, db):
    """
    used to test the api endpoints.
    db fixture is included to call db.create_all in db fixture
    """
    client = app.test_client()

    with app.app_context():
        yield client
