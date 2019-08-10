import pytest
from app import create_app, db as _db
from app.models import AppUser, Team, TeamMember


MOCK_TOKEN = "MOCK_TOKEN"
FIR_AUTH_ID = "FIR_AUTH_ID"


@pytest.fixture(scope="session")
def app():
    app = create_app(test=True)
    return app


@pytest.fixture(scope="session")
def db(app):
    _db.app = app
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope="session")
def client(app, db):
    """
    used to test the api endpoints.
    db fixture is included to call db.create_all in db fixture
    """
    client = app.test_client()

    with app.app_context():
        yield client


@pytest.fixture
def session(db):
    yield db.session

    # cleanup session objects added by tests
    db.session.rollback()

    # erase data committed by source code
    # https://stackoverflow.com/questions/4763472/sqlalchemy-clear-database-content-but-dont-drop-the-schema
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()
    db.session.close()


@pytest.fixture
def user1(session):
    user1 = AppUser()
    session.add(user1)
    session.flush()
    return user1


@pytest.fixture
def team1(session, user1):
    team1 = Team(founder=user1, name="Tigers")
    session.add(team1)
    session.flush()
    return team1


@pytest.fixture
def team_member1(session, user1, team1):
    team_member1 = TeamMember(user=user1, team=team1, inviter=user1, status="ACTIVE")
    session.add(team_member1)
    session.flush()
    return team_member1


# @pytest.fixture
def get_auth_token(some_client):
    headers = {"Authorization": MOCK_TOKEN}
    response = some_client.get("/api/auth_token", headers=headers)

    return f"token {response.get_json()['auth_token']}"
