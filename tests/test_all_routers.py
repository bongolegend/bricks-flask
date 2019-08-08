"""Module to test routers"""
import datetime as dt
import os

from app.constants import US_TIMEZONES, RouterNames, Statuses
from app.get_router import get_router
from app.models import AppUser, Exchange, Notification, Point, Task, Team, TeamMember
from tests.base_test_case import BaseTestCase
from tests.constants import TEST_TEAM_ID


class TestAllRouters(BaseTestCase):
    inviter_number = os.environ.get("TEST_FROM_NUMBER")

    @classmethod
    def get_routers(self):
        routers = get_router()
        # don't test this router
        routers.pop(RouterNames.INIT_ONBOARDING_INVITED)
        return routers

    def setUp(self):
        super().setUp()
        # add a user
        self.mitch = AppUser(
            phone_number=self.inviter_number,
            username="mitch",
            timezone=US_TIMEZONES["b"],
        )

        self.db.session.add(self.mitch)
        # self.db.session.add(self.blair)

        # add a notif
        self.notif = Notification(
            router=RouterNames.DID_YOU_DO_IT,
            hour=21,
            minute=0,
            active=True,
            user=self.mitch,
        )

        self.db.session.add(self.notif)

        # add exchange
        self.exchange = Exchange(
            router=RouterNames.DID_YOU_DO_IT,
            outbound="Did you do it?",
            user=self.mitch,
            created=dt.datetime.now() - dt.timedelta(days=10),
        )

        self.db.session.add(self.exchange)

        # add point
        self.point = Point(value=10, user=self.mitch)

        # add task
        self.task = Task(
            description="Win today",
            due_date=dt.datetime.now(),
            active=True,
            exchange=self.exchange,
            user=self.mitch,
        )

        self.db.session.add(self.task)

        self.inteam = Team(id=TEST_TEAM_ID, founder=self.mitch, name="inteam")
        self.db.session.add(self.inteam)

        self.pendingteam = Team(founder=self.mitch, name="pendingteam")
        self.db.session.add(self.pendingteam)

        self.mitch_member = TeamMember(
            user=self.mitch,
            team=self.inteam,
            inviter=self.mitch,
            status=Statuses.ACTIVE,
        )
        self.db.session.add(self.mitch_member)

        self.mitch_member2 = TeamMember(
            user=self.mitch,
            team=self.pendingteam,
            inviter=self.mitch,
            status=Statuses.PENDING,
        )
        self.db.session.add(self.mitch_member2)
