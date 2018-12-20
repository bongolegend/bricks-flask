"""Module to test notification sending"""
import datetime as dt
import pytz
from tests.config_test import BaseTestCase
from app.models import AppUser, Exchange, Task, Team, TeamMember, Notification, Point
from app.routers import DidYouDoIt, MorningConfirmation
from app.tools import get_router
from app.constants import US_TIMEZONES, Statuses


class TestNotifications(BaseTestCase):
    mitch_tz = US_TIMEZONES['b']
    local_now = dt.datetime.now(tz=pytz.timezone(mitch_tz))
    number = '+13124505311'

    def setUp(self):
        super().setUp()
        # add a user
        self.mitch = AppUser(
            phone_number=self.number, 
            username='Mitch',
            timezone=self.mitch_tz)

        self.db.session.add(self.mitch)

        # add exchange
        self.exchange = Exchange(
            router = DidYouDoIt.__name__,
            outbound = 'Did you do it?',
            user = self.mitch)

        self.db.session.add(self.exchange)

        # add a notif
        self.did_you_do_it_notif = Notification(
            router = DidYouDoIt.__name__,
            body = DidYouDoIt.outbound,
            hour = self.local_now.hour,
            minute = self.local_now.minute,
            active = True,
            user = self.mitch)
        
        self.db.session.add(self.did_you_do_it_notif)

        self.morning_conf_notif = Notification(
            router = MorningConfirmation.__name__,
            body = MorningConfirmation.outbound,
            hour = self.local_now.hour,
            minute = self.local_now.minute,
            active = True,
            user = self.mitch)
        
        self.db.session.add(self.morning_conf_notif)

        # add task
        self.task = Task(
            description='Win today',
            due_date = dt.datetime.now()+ dt.timedelta(minutes=1),
            active = True,
            exchange = self.exchange,
            user = self.mitch)
        
        self.db.session.add(self.task)

    def test_notification(self):
        '''send one notification whose time corresponds with now'''
        response = self.client.get('/notifications')

        print(response.data)