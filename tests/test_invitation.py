'''Separate test for InitOnboardingInvited'''
import datetime as dt
import os
from tests.base_test_case import BaseTestCase
from app.models import AppUser, Exchange, Task, Team, TeamMember, Point
from app.routers import InitOnboardingInvited
from app.constants import US_TIMEZONES, Statuses


class TestInitOnboardingInvited(BaseTestCase):
    inviter_number = os.environ.get('TEST_FROM_NUMBER')
    invitee_number = os.environ.get('TEST_TO_NUMBER')

    @classmethod
    def get_routers(self):
        return {InitOnboardingInvited.__name__ : InitOnboardingInvited}

    def setUp(self):
        super().setUp()

        # the scenario is Mitch has received an invitation to a team
        # He has never used Bricks before
        self.inviter = AppUser(
            phone_number=self.inviter_number,
            username='Jo',
            timezone=US_TIMEZONES['b'])

        self.mitch = AppUser(
            phone_number=self.invitee_number,
            username='Mitch',
            timezone=US_TIMEZONES['b'])

        self.team = Team(
            founder=self.inviter,
            name='The Cherrys')
        
        self.inviter_member = TeamMember(
            user=self.inviter,
            team=self.team,
            inviter=self.inviter,
            status=Statuses.ACTIVE)
        
        self.invitee_member = TeamMember(
            user=self.mitch,
            team=self.team,
            inviter=self.inviter,
            status=Statuses.PENDING)
        
        self.exchange = Exchange(
            user=self.mitch,
            router=InitOnboardingInvited.__name__)
        
        self.db.session.add(self.inviter)
        self.db.session.add(self.mitch)
        self.db.session.add(self.team)
        self.db.session.add(self.inviter_member)
        self.db.session.add(self.invitee_member)
