import unittest
from app import create_app, db 
from app import models


def clean_db(db):
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())


class BaseTestCase(unittest.TestCase):
    db = None

    @classmethod
    def setUpClass(cls):
        super(BaseTestCase, cls).setUpClass()
        cls.app = create_app(test=True)
        cls.client = cls.app.test_client()
        cls.db = db
        cls.db.app = cls.app
        cls.db.create_all()

    @classmethod
    def tearDownClass(cls):
        cls.db.session.close()
        cls.db.drop_all()
        super(BaseTestCase, cls).tearDownClass()

    def setUp(self):
        super(BaseTestCase, self).setUp()

        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        clean_db(self.db)

    def tearDown(self):
        self.db.session.rollback()
        self.app_context.pop()
        
        # TODO(Nico) figure out how to clear the db, as rolling back the session doesn't work if your code
        models.Point.query.delete()
        models.Task.query.delete()
        models.TeamMember.query.delete()
        models.Team.query.delete()
        models.Notification.query.delete()
        models.Exchange.query.delete()
        models.AppUser.query.delete()

        super(BaseTestCase, self).tearDown()