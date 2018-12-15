"""Module to test routers"""
import datetime as dt
from tests.config_test import BaseTestCase
from app.models import AppUser, Exchange, Task, Team, TeamMember, Notification, Point
from app.routers import get_router, DidYouDoIt
from app.constants import US_TIMEZONES, Statuses


class TestAllRouters(BaseTestCase):
    number = '+11234567890'

    def setUp(self):
        super().setUp()
        # add a user
        self.mitch = AppUser(
            phone_number=self.number, 
            username='Mitch',
            timezone=US_TIMEZONES['b'])

        self.db.session.add(self.mitch)

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
            user = self.mitch)

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
        self.teammember = TeamMember(
            user = self.mitch,
            team = self.team,
            invited_by = self.mitch,
            status = Statuses.PENDING)
        
        self.db.session.add(self.teammember)

    
    def test_all_routers(self):
        for router_name in get_router():
            print("TESTING ROUTER: ", router_name)
            exchange = Exchange(router=router_name, user=self.mitch)
            self.db.session.add(exchange)
            response = self.client.post('/sms', data=dict(Body='', From=self.number))
    