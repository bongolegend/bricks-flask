import os
from tests.base_test_case import BaseTestCase
from app.actions import multiplayer
from sqlalchemy.orm.exc import NoResultFound
from app.constants import US_TIMEZONES, Statuses
from app.models import AppUser, Team, TeamMember
from app.routers import InitOnboardingInvited, YouWereInvited

class TestMultiplayer(BaseTestCase):
    inviter_number = os.environ.get('TEST_FROM_NUMBER')
    secondary_number = os.environ.get('TEST_TO_NUMBER')
    third_number = os.environ.get('EXTRA_NUMBER_1')
    fourth_number = os.environ.get('EXTRA_NUMBER_2')
    fifth_number = os.environ.get('EXTRA_NUMBER_3')
    sixth_number = os.environ.get('EXTRA_NUMBER_4')

    def setUp(self):
        super().setUp()

        self.mitch = AppUser(
            phone_number=self.inviter_number, 
            username='mitch',
            timezone=US_TIMEZONES['b'])
        self.db.session.add(self.mitch)

        self.billy = AppUser(
            phone_number=self.secondary_number, 
            username='billy',
            timezone=US_TIMEZONES['b'])
        self.db.session.add(self.billy)

        self.jonah = AppUser(
            phone_number=self.third_number, 
            username='jonah',
            timezone=US_TIMEZONES['b'])
        self.db.session.add(self.jonah)

        self.allie = AppUser(
            phone_number=self.fourth_number, 
            username='allie',
            timezone=US_TIMEZONES['b'])
        self.db.session.add(self.allie)

        self.winnie = AppUser(
            phone_number=self.fifth_number, 
            username='winnie',
            timezone=US_TIMEZONES['b'])
        self.db.session.add(self.winnie)

        self.full_team = Team(
            founder = self.mitch,
            name = 'The Fulls')
        self.db.session.add(self.full_team)

        self.open_team = Team(
            founder = self.mitch,
            name = 'The Opens')
        self.db.session.add(self.open_team)

        self.mitch_member = TeamMember(
            user = self.mitch,
            team = self.full_team,
            inviter = self.mitch,
            status = Statuses.ACTIVE)       
        self.db.session.add(self.mitch_member)

        self.mitch_member_2 = TeamMember(
            user = self.mitch,
            team = self.open_team,
            inviter = self.mitch,
            status = Statuses.ACTIVE)       
        self.db.session.add(self.mitch_member_2)

        self.billy_member = TeamMember(
            user = self.billy,
            team = self.full_team,
            inviter = self.mitch,
            status = Statuses.ACTIVE)       
        self.db.session.add(self.billy_member)

        self.jonah_member = TeamMember(
            user = self.jonah,
            team = self.full_team,
            inviter = self.mitch,
            status = Statuses.ACTIVE)       
        self.db.session.add(self.jonah_member)

        self.allie_member = TeamMember(
            user = self.allie,
            team = self.full_team,
            inviter = self.mitch,
            status = Statuses.ACTIVE)       
        self.db.session.add(self.allie_member)

        self.winnie_member = TeamMember(
            user = self.winnie,
            team = self.full_team,
            inviter = self.mitch,
            status = Statuses.ACTIVE)       
        self.db.session.add(self.winnie_member)

        self.db.session.commit()

        self.mitch = self.mitch.to_dict()
        self.billy = self.billy.to_dict()
    

    def test_team_full(self):
        '''raise error if user selects a team that is already full'''
        inbound = (self.full_team.id, self.sixth_number)

        self.assertRaises(
            AssertionError,
            multiplayer.insert_member,
            self.mitch, 
            inbound, 
            InitOnboardingInvited, 
            YouWereInvited)

    def test_team_open(self):
        '''allow invitee to be added to an open team'''
        inbound = (self.open_team.id, self.sixth_number)
        multiplayer.insert_member(
            self.mitch, 
            inbound, 
            InitOnboardingInvited, 
            YouWereInvited)
    
    def test_get_open_teams(self):
        '''assert that there is only one open team'''
        teams = multiplayer.get_open_teams(self.mitch)
        assert len(teams) == 1
    
    def test_str_open_teams(self):
        '''make sure the func runs'''
        result = multiplayer.str_open_teams(self.mitch)
        print(result)