"""Module to test routers"""
import datetime as dt
import os
import unittest
from tests.config_test import BaseTestCase
from app.models import AppUser, Exchange, Task, Team, TeamMember, Notification, Point
from app import models
from app.routers import DidYouDoIt, InitOnboardingInvited
from app.constants import US_TIMEZONES, Statuses
from app import parsers
from app.get_router import get_router


class TestAllRouters(BaseTestCase):
    inviter_number = os.environ.get('TEST_FROM_NUMBER')

    @classmethod
    def get_routers(self):
        routers = get_router()
        routers.pop(InitOnboardingInvited.__name__)
        return routers

    def setUp(self):
        super().setUp()
        # add a user
        self.mitch = AppUser(
            phone_number=self.inviter_number, 
            username='mitch',
            timezone=US_TIMEZONES['b'])

        self.db.session.add(self.mitch)
        # self.db.session.add(self.blair)

        # add a notif
        self.notif = Notification(
            router = DidYouDoIt.__name__,
            body = DidYouDoIt.outbound,
            hour = 21,
            minute = 0,
            active = True,
            user = self.mitch)
        
        self.db.session.add(self.notif)

        # add exchange
        self.exchange = Exchange(
            router = DidYouDoIt.__name__,
            outbound = 'Did you do it?',
            user = self.mitch,
            created = dt.datetime.now() - dt.timedelta(days=10))

        self.db.session.add(self.exchange)

        # add point
        self.point = Point(
            value = 10,
            user = self.mitch)    

        # add task
        self.task = Task(
            description='Win today',
            due_date = dt.datetime.now(),
            active = True,
            exchange = self.exchange,
            user = self.mitch)
        
        self.db.session.add(self.task)

        # add team
        self.team = Team(
            founder = self.mitch,
            name = 'The Cherrys')

        self.db.session.add(self.team)

        # add teammember
        self.mitch_member = TeamMember(
            user = self.mitch,
            team = self.team,
            invited_by = self.mitch,
            status = Statuses.PENDING)
        
        self.db.session.add(self.mitch_member)
    