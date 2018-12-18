import sys, inspect
from app import parsers, actions, conditions
from app.constants import Outbounds, Points


class Router:
    pre_actions = None
    actions = None
    inbound_format = parsers.ANY
    confirmation = None
    participation_points = Points.DEFAULT

    @classmethod
    def __init__(self, **kwargs):
        self.name = self.__name__

    @classmethod
    def next_router(self, **kwargs):
        return MainMenu
    
    @classmethod
    def parse(self, inbound, **kwargs):
        return parsers.parse(inbound, self.inbound_format)
    
    @classmethod
    def run_pre_actions(self, user, exchange, **kwargs):
        if self.pre_actions is not None:
            result_dict = dict()
            for action in self.pre_actions:
                result = action(
                    current_router=self,
                    user=user,
                    exchange=exchange)
                print('PRE_ACTION EXECUTED: ', action.__name__)
                result_dict[action.__name__] = result
            return result_dict
        return dict()

    @classmethod
    def run_actions(self, user, exchange, inbound, **kwargs):
        if self.actions is not None:
            result_dict = dict()
            for action in self.actions:
                result = action(
                    current_router=self,
                    inbound=inbound, 
                    user=user,
                    exchange=exchange)
                print('ACTION EXECUTED: ', action.__name__)
                result_dict[action.__name__] = result
            return result_dict
        return dict()
    
    @classmethod
    def insert_points(self, user, **kwargs):
        '''Receive participation points'''
        if self.participation_points > 0:
            actions.insert_points(user, self.participation_points)
            return Points.EARNED_MESSAGE.format(points=self.participation_points)
        else:
            return str()


class InitOnboarding(Router):

    @classmethod
    def next_router(self, **kwargs):
        return Welcome


class Welcome(Router):
    outbound = "Hey! Welcome to Bricks, a tool that helps you get stuff done. Would you like to create an account? (y/n)"
    inbound_format = parsers.YES_NO

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return EnterUsername
        else:
            return Goodbye


class EnterUsername(Router):
    outbound = 'Please enter a username:'
    actions = (actions.update_username,)
    confirmation = "Your username is set."

    @classmethod
    def next_router(self, **kwargs):
        return HowItWorks

class Goodbye(Router):
    outbound = "Sorry to hear that. Goodbye."
    
    @classmethod
    def next_router(self, **kwargs):
        return Welcome


class HowItWorks(Router):
    outbound = Outbounds.HOW_IT_WORKS
    inbound_format = parsers.YES_NO

    @classmethod
    def next_router(self, inbound, user, **kwargs):
        if inbound == 'no':
            return ContactSupport
        elif inbound == 'yes':
            if conditions.timezone_set(user):
                return MainMenu
            else:
                return Timezone


class ContactSupport(Router):
    outbound =  "Text me at 3124505311 and I'll walk you through it. Type anything to continue."

    @classmethod
    def next_router(self, user, **kwargs):
        if conditions.timezone_set(user):
            return MainMenu
        else:
            return Timezone


class MainMenu(Router):
    outbound = Outbounds.MAIN_MENU
    inbound_format = parsers.MULTIPLE_CHOICE

    @classmethod
    def next_router(self, inbound, user, **kwargs):
        if inbound == 'a':
            if conditions.is_afternoon(user):
                return ChooseTomorrowTask
            else:
                return ChooseTask
        elif inbound == 'b':
            return Timezone
        elif inbound == 'c':
            return HowItWorks
        elif inbound == 'd':
            return CurrentPoints
        elif inbound == 'e':
            return Leaderboard
        elif inbound == 'f':
            return CreateTeam
        elif inbound == 'g':
            if conditions.is_member_of_team(user):
                return AddMember
            else:
                return CreateTeam


class Timezone(Router):
    outbound = Outbounds.WHAT_TIMEZONE
    actions = (actions.update_timezone,)
    inbound_format = parsers.MULTIPLE_CHOICE
    confirmation = "Your timezone is set."

    @classmethod
    def next_router(self, user, **kwargs):
        if conditions.task_chosen(user):
            return MainMenu
        elif conditions.is_afternoon(user):
            return ChooseTomorrowTask
        else:
            return ChooseTask


class ChooseTask(Router):
    outbound = "What's the most important thing you want to get done today?"
    participation_points = Points.CHOOSE_TASK
 
    @classmethod   
    def next_router(self, **kwargs):
        return StateNightFollowup
    
    @classmethod
    def run_actions(self, user, exchange, inbound):
        insert_notif_result = actions.insert_notifications(
            user, 
            self, 
            MorningConfirmation, 
            DidYouDoIt)

        insert_task_result = actions.insert_task(
            user, 
            exchange, 
            inbound, 
            self, 
            ChooseTomorrowTask,
            DidYouDoIt)
        
        return {
            actions.insert_notifications.__name__ : insert_notif_result,
            actions.insert_task.__name__ : insert_task_result}
    
    @classmethod
    def insert_points(self, user, **kwargs):
        '''You only get points if you havent already chosen a task for today'''
        if not conditions.task_chosen(user):
            actions.insert_points(user, self.participation_points)
            return Points.EARNED_MESSAGE.format(points=self.participation_points)
        else:
            return Points.ALREADY_EARNED_MESSAGE
        


class CurrentPoints(Router):
    pre_actions = (actions.query_points,)
    outbound = "You currently have +{query_points} pt."


class StateNightFollowup(Router):
    outbound = "I'll text you tonight at 9 pm to follow up. Good luck."


class ChooseTomorrowTask(Router):
    outbound = "What's the most important thing you want to get done tomorrow?"
    participation_points = Points.CHOOSE_TASK

    @classmethod
    def next_router(self, **kwargs):
        return StateMorningFollowup
    
    @classmethod
    def run_actions(self, user, exchange, inbound, **kwargs):
        insert_notif_result = actions.insert_notifications(
            user, 
            ChooseTask, 
            MorningConfirmation, 
            DidYouDoIt)

        insert_result = actions.insert_task(
            user, 
            exchange, 
            inbound, 
            ChooseTask, 
            ChooseTomorrowTask,
            DidYouDoIt)

        return {
            actions.insert_notifications.__name__ : insert_notif_result,
            actions.insert_task.__name__ : insert_result}
    
    @classmethod
    def insert_points(self, user, **kwargs):
        '''You only get points if you havent already chosen a task for tomorrow'''
        if not conditions.task_chosen(user, tomorrow=True):
            actions.insert_points(user, self.participation_points)
            return Points.EARNED_MESSAGE.format(points=self.participation_points)
        else:
            return Points.ALREADY_EARNED_MESSAGE 


class DidYouDoIt(Router):
    outbound = 'Did you stack your brick today? (y/n)'
    inbound_format = parsers.YES_NO
    # participation_points = Points.DID_YOU_DO_IT

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return CompletionPoint
        elif inbound == 'no':
            return NoCompletion
    
    @classmethod
    def run_actions(self, user, inbound, **kwargs):
        if inbound == 'yes':
            result = actions.insert_points(user, Points.TASK_COMPLETED)
        else:
            result = 0
        return {actions.insert_points.__name__ : result}


# TODO combine this with the one below it
# TODO rename this to congrats
class CompletionPoint(Router):
    pre_actions = (actions.query_points,)
    outbound = "Congrats! You earned +%s points. You now have {query_points} points. Do you want to choose tomorrow's task now? (y/n)" % Points.TASK_COMPLETED
    inbound_format = parsers.YES_NO
    participation_points = Points.CHOOSE_TASK

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return ChooseTomorrowTask
        elif inbound == 'no':
            return StateMorningFollowup


class NoCompletion(Router):
    pre_actions = (actions.query_points,)
    outbound = "All good. Just make tomorrow count. You currently have {query_points} points. Do you want to choose tomorrow's task now? (y/n)"
    inbound_format = parsers.YES_NO
    participation_points = Points.CHOOSE_TASK

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return ChooseTomorrowTask
        elif inbound == 'no':
            return StateMorningFollowup


class StateMorningFollowup(Router):
    outbound =  "Great. I'll message you tomorrow at 8 am to confirm."


class MorningConfirmation(Router):
    outbound = "Are you still planning to do this task today: {query_latest_task}? (y/n)"
    inbound_format = parsers.YES_NO
    participation_points = Points.CHOOSE_TASK

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return StateNightFollowup
        elif inbound == 'no':
            return ChooseTask
    
    @classmethod
    def run_pre_actions(self, user, **kwargs):
        query_task_result = actions.query_latest_task(user, ChooseTask, ChooseTomorrowTask)

        return {actions.query_latest_task.__name__ : query_task_result}


class Leaderboard(Router):
    pre_actions = (actions.leaderboard,)
    outbound = "{leaderboard}"
    

class CreateTeam(Router):
    outbound = "What do you want to name your team?"
    actions = (actions.insert_team,)
    confirmation = "Team created."

    @classmethod
    def next_router(self, **kwargs):
        return AddMember


class AddMember(Router):
    pre_actions = (actions.list_teams,)
    outbound = """To invite a friend, enter the team number and your friend's phone number, e.g. "25, 123-456-7890". Your current teams:\n{list_teams}"""
    inbound_format = parsers.ADD_MEMBER
    confirmation = "Sent an invitation to your friend. I'll let you know when they respond."

    @classmethod
    def run_actions(self, user, inbound, **kwargs):
        result = actions.insert_member(user, inbound, InitOnboardingInvited, YouWereInvited)
        return {actions.insert_member.__name__ : result}


class InitOnboardingInvited(Router):
    pre_actions = (actions.query_last_invitation,)
    outbound = "Hey! Your friend {query_last_invitation[0]} invited you to join their team {query_last_invitation[1]}, on the Bricks app. Do you want to accept? (y/n)"
    inbound_format = parsers.YES_NO
    actions = (actions.confirm_team_member, actions.notify_inviter)

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return EnterUsername
        else:
            return Goodbye


class YouWereInvited(Router):
    pre_actions = (actions.query_last_invitation,)
    outbound = "Hey! Your friend {query_last_invitation[0]} invited you to join their team {query_last_invitation[1]}. Do you want to accept? (y/n)"
    inbound_format = parsers.YES_NO
    actions = (actions.confirm_team_member, actions.notify_inviter)

    # @classmethod
    # def next_router(self, inbound, **kwargs):
    #     if inbound == 'yes':
    #         return IntroToTeam
    #     else:
    #         return MainMenu


# class IntroToTeam(Router):
#     pre_actions = (actions.intro_to_team,)
#     outbound = "Current team members:\n{intro_to_team}\n I will notify you of the tasks they choose tomorrow"


class InvitationAccepted(Router):
    outbound = "Your friend accepted your invitation!" # TODO(Nico) specify who and what team


class InvitationRejected(Router):
    outbound = "Your friend rejected your invitation."



def get_router(router_name=None):
    '''return the router associated with the router_name, or return a dict of routers'''

    all_classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
    
    # only keep those that have Router as parent class
    routers = dict()
    for name, cls in all_classes:
        if issubclass(cls, Router) and cls is not Router:
            routers[name] = cls

    if router_name:
        assert router_name in routers, "This router name is not implemented as a router"
        return routers[router_name]
    else:
        return routers
