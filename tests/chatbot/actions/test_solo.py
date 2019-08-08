import os
import datetime as dt
from tests.base_test_case import BaseTestCase
from app.actions import solo
from app.constants import US_TIMEZONES, Statuses, RouterNames
from app.models import AppUser, Task, Exchange


class TestSolo(BaseTestCase):
    inviter_number = os.environ.get("TEST_FROM_NUMBER")

    def setUp(self):
        super().setUp()

        now = dt.datetime.now()

        self.mitch = AppUser(
            phone_number=self.inviter_number,
            username="mitch",
            timezone=US_TIMEZONES["b"],
        )
        self.db.session.add(self.mitch)

        self.exchange = Exchange(router=RouterNames.DID_YOU_DO_IT, user=self.mitch)
        self.db.session.add(self.exchange)

        self.task1 = Task(
            description="clean",
            due_date=now - dt.timedelta(days=6),
            active=True,
            user=self.mitch,
            exchange=self.exchange,
        )
        self.db.session.add(self.task1)

        self.task2 = Task(
            description="cook",
            due_date=now - dt.timedelta(days=8),
            active=True,
            user=self.mitch,
            exchange=self.exchange,
        )
        self.db.session.add(self.task2)

        self.db.session.commit()

        self.mitch = self.mitch.to_dict()

    def test_get_past_tasks(self):
        """assert that tasks from the past week only get queried"""
        tasks = solo.get_past_tasks(self.mitch)

        assert len(tasks) == 1
