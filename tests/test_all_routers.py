"""Module to test routers"""
import datetime as dt
import os
import unittest
from tests.config_test import BaseTestCase
from app.models import AppUser, Exchange, Task, Team, TeamMember, Notification, Point
from app import models
from app.routers import DidYouDoIt
from app.constants import US_TIMEZONES, Statuses
from app import parsers


def generator(router, inbound=str()):
    '''function that returns one test function per router'''
    def test(self):
        print(f"""
=============================
TESTING ROUTER: {router.__name__}
TESTING INBOUND: {inbound}
=============================
        """)
        exchange = Exchange(router=router.__name__, user=self.mitch)
        self.db.session.add(exchange)
        response = self.client.post('/sms', data=dict(Body=inbound, From=self.number))

    return test


class TestAllRouters(BaseTestCase):
    number = os.environ.get('TEST_FROM_NUMBER')

    def setUp(self):
        super().setUp()
        # add a user
        self.mitch = AppUser(
            phone_number=self.number, 
            username='Mitch',
            timezone=US_TIMEZONES['b'])
        
        # self.blair = AppUser(
        #     phone_number=self.number, 
        #     username='Blair',
        #     timezone=US_TIMEZONES['b'])

        self.db.session.add(self.mitch)
        # self.db.session.add(self.blair)

        # add a notif
        # self.notif = Notification(
        #     router = DidYouDoIt.__name__,
        #     body = DidYouDoIt.outbound,
        #     hour = 21,
        #     minute = 0,
        #     active = True,
        #     user = self.mitch)
        
        # self.db.session.add(self.notif)

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
        
        # add teammember
        # self.blair_member = TeamMember(
        #     user = self.blair,
        #     team = self.team,
        #     invited_by = self.mitch,
        #     status = Statuses.PENDING)
        
        self.db.session.add(self.mitch_member)
        # self.db.session.add(self.blair_member)

    def tearDown(self):
        super().tearDown()
        # TODO(Nico) figure out how to clear the db, as rolling back the session doesn't work if your code
        models.Point.query.delete()
        models.Task.query.delete()
        models.TeamMember.query.delete()
        models.Team.query.delete()
        models.Notification.query.delete()
        models.Exchange.query.delete()
        models.AppUser.query.delete()