import os
import datetime as dt
from tests.base_test_case import BaseTestCase
from app.actions import settings
from app.constants import US_TIMEZONES, RouterNames
from app.models import AppUser, Exchange, Task

class TestSettings(BaseTestCase):
    inviter_number = os.environ.get('TEST_FROM_NUMBER')
    due_date =  dt.datetime.now() + dt.timedelta(days=1)
    description = "Do my laundry"

    def setUp(self):
        super().setUp()

        self.mitch = AppUser(
            phone_number=self.inviter_number, 
            username='mitch',
            timezone=US_TIMEZONES['a'])
        self.db.session.add(self.mitch)

        self.exchange = Exchange(
            router = RouterNames.DID_YOU_DO_IT,
            outbound = 'Did you do it?',
            user = self.mitch)
        self.db.session.add(self.exchange)

        self.task = Task(
            description = self.description,
            due_date = self.due_date,
            active = True,
            user = self.mitch,
            exchange = self.exchange)
        self.db.session.add(self.task)

        self.db.session.commit()

        self.mitch = self.mitch.to_dict()
    
    def test_update_timezone(self):
        '''test that when you update timezone, the due date on the task gets updated correctly'''
        valid_inbound = 'd'

        settings.update_timezone(valid_inbound, self.mitch)

        expected_due_date = self.due_date - dt.timedelta(hours=3)

        task = self.db.session.query(Task).filter(Task.description == self.description).one()
        
        assert task.due_date == expected_due_date
