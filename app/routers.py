import sys, inspect
from app import parsers, conditions
from app.actions import solo, multiplayer, settings
from app.constants import Outbounds, Points
# from app.routers.base import BaseRouter


class BaseRouter:
    pre_actions = None
    actions = None
    inbound_format = parsers.ANY
    confirmation = None
    participation_points = Points.DEFAULT

    @classmethod
    def __init__(self, **kwargs):
        '''make the class name available on the instant, useful forl referencing'''
        self.name = self.__name__

    @classmethod
    def next_router(self, **kwargs):
        '''send to the Main Menu router by default'''
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
                    exchange=exchange,
                    **kwargs)
                print('ACTION EXECUTED: ', action.__name__)
                result_dict[action.__name__] = result
            return result_dict
        return dict()
    
    @classmethod
    def insert_points(self, user, **kwargs):
        '''Receive participation points'''
        if self.participation_points > 0:
            solo.insert_points(user, self.participation_points)
            return Points.EARNED_MESSAGE.format(points=self.participation_points)
        else:
            return str()


class InitOnboarding(BaseRouter):
    @classmethod
    def next_router(self, **kwargs):
        return Welcome


class Welcome(BaseRouter):
    outbound = "Hey! Welcome to Bricks, a tool that helps you get stuff done. Would you like to create a settings? (y/n)"
    inbound_format = parsers.YES_NO

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return EnterUsername
        else:
            return GoodbyeFeedback


class EnterUsername(BaseRouter):
    outbound = 'Please enter a username, preferably one that your friends will recognize:'
    actions = (settings.update_username,)
    confirmation = "Your username is set."

    @classmethod
    def next_router(self, user, **kwargs):
        if conditions.timezone_set(user):
            return MainMenu
        else:
            return Timezone


class GoodbyeFeedback(BaseRouter):
    outbound = "Sorry to hear that. Why don't you want to use this app?"
    
    @classmethod
    def next_router(self, **kwargs):
        return ThanksForFeedback


class ThanksForFeedback(BaseRouter):
    outbound = "Thanks for your feedback!"

    @classmethod
    def next_router(self, **kwargs):
        return Welcome


class HowItWorks(BaseRouter):
    outbound = Outbounds.HOW_IT_WORKS
    inbound_format = parsers.YES_NO

    @classmethod
    def next_router(self, inbound, user, **kwargs):
        if inbound == 'no':
            return ContactSupport
        elif inbound == 'yes':
            if conditions.is_new_user(user):
                return InitOnboardingInvited
            else:
                return MainMenu


class ContactSupport(BaseRouter):
    outbound =  "Text the developer at 3124505311 and I'll walk you through it. Type anything to continue."

    @classmethod
    def next_router(self, user, **kwargs):
        if conditions.timezone_set(user):
            return MainMenu
        elif conditions.is_new_user(user):
            return InitOnboardingInvited
        else:
            return Timezone


class MainMenu(BaseRouter):
    pre_actions = (solo.get_username, solo.get_total_points)
    outbound = Outbounds.MAIN_MENU
    inbound_format = parsers.MAIN_MENU

    @classmethod
    def next_router(self, inbound, user, **kwargs):
        if inbound == 'a':
            if conditions.is_afternoon(user):
                return ChooseTomorrowTask
            else:
                return ChooseTask
        elif inbound == 'b':
            if conditions.is_member_of_team(user):
                return AddMember
            else:
                return CreateTeam
        elif inbound == 'c':
            return CreateTeam            
        elif inbound == 'd':
            return ViewTeamMembers
        elif inbound == 'e':
            return LeaderboardMenu
        elif inbound == 'f':
            return Settings


class LeaderboardMenu(BaseRouter):
    outbound = Outbounds.LEADERBOARD_MENU
    inbound_format = parsers.MULTIPLE_CHOICE

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'a':
            return TeamLeaderboard
        elif inbound == 'b':
            return TrapDoor
        elif inbound == 'c':
            return Leaderboard
        elif inbound == 'd':
            return MainMenu
        

class Settings(BaseRouter):
    outbound = Outbounds.SETTINGS
    inbound_format = parsers.MULTIPLE_CHOICE

    @classmethod
    def next_router(self, inbound, user, **kwargs):
        if inbound == 'a':
            return Timezone
        elif inbound == 'b':
            return EnterUsername
        elif inbound == 'c':
            return LeaveTeam
        elif inbound == 'd':
            return HowItWorks
        elif inbound == 'e':
            return MainMenu


class Timezone(BaseRouter):
    outbound = Outbounds.WHAT_TIMEZONE
    actions = (settings.update_timezone,)
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


class ChooseTask(BaseRouter):
    outbound = "What's your top task for today?"
    actions = (solo.insert_task, multiplayer.notify_team_members)
    participation_points = Points.CHOOSE_TASK

 
    @classmethod   
    def next_router(self, **kwargs):
        return StateNightFollowup
    
    @classmethod
    def insert_points(self, user, **kwargs):
        '''You only get points if you havent already chosen a task for today'''
        if not conditions.task_chosen(user):
            solo.insert_points(user, self.participation_points)
            return Points.EARNED_MESSAGE.format(points=self.participation_points)
        else:
            return Points.ALREADY_EARNED_MESSAGE


class StateNightFollowup(BaseRouter):
    outbound = "I'll text you tonight at 9 pm to follow up. Good luck."


class ChooseTomorrowTask(BaseRouter):
    outbound = "What's your top task for tomorrow?"
    actions = (solo.insert_task, multiplayer.notify_team_members)
    participation_points = Points.CHOOSE_TASK

    @classmethod
    def next_router(self, **kwargs):
        return StateMorningFollowup
    
    @classmethod
    def insert_points(self, user, **kwargs):
        '''You only get points if you havent already chosen a task for tomorrow'''
        if not conditions.task_chosen(user, tomorrow=True):
            solo.insert_points(user, self.participation_points)
            return Points.EARNED_MESSAGE.format(points=self.participation_points)
        else:
            return Points.ALREADY_EARNED_MESSAGE 


class DidYouDoIt(BaseRouter):
    pre_actions = (solo.get_latest_task,)
    outbound = 'On a scale of 0 to 10, how well did you complete this? {get_latest_task}'
    inbound_format = parsers.ZERO_TO_TEN

    @classmethod
    def insert_points(self, inbound, user, **kwargs):
        '''insert points based on inbound and send a confirmation message.'''
        solo.insert_points(user, inbound)
        return Points.EARNED_MESSAGE.format(points=inbound)

    @classmethod
    def next_router(self, inbound, **kwargs):
        return TaskCompleted

    
class TaskCompleted(BaseRouter):
    pre_actions = (solo.get_total_points,)
    outbound = "You now have {get_total_points} points. Do you want to choose tomorrow's task now? (y/n)"
    inbound_format = parsers.YES_NO
    participation_points = Points.CHOOSE_TASK

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return ChooseTomorrowTask
        elif inbound == 'no':
            return StateMorningChooseTask


class StateMorningFollowup(BaseRouter):
    outbound =  "Great. I'll message you tomorrow at 8 am to remind you."


class StateMorningChooseTask(BaseRouter):
    outbound = "No problem. I'll just ask you tomorrow morning."



class MorningConfirmation(BaseRouter):
    pre_actions = (solo.get_latest_task,)
    outbound = "Are you still planning to do this task today: {get_latest_task}? (y/n)"
    inbound_format = parsers.YES_NO
    participation_points = Points.CHOOSE_TASK

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return StateNightFollowup
        elif inbound == 'no':
            return ChooseTask


class Leaderboard(BaseRouter):
    pre_actions = (multiplayer.get_leaderboard,)
    outbound = "{get_leaderboard}"

    @classmethod
    def next_router(self, **kwargs):
        return LeaderboardMenu
    

class CreateTeam(BaseRouter):
    outbound = "Enter a name for a new team:"
    actions = (multiplayer.insert_team,)
    confirmation = "Team created."

    @classmethod
    def next_router(self, **kwargs):
        return AddMember


class AddMember(BaseRouter):
    pre_actions = (multiplayer.str_open_teams,)
    outbound = """Your teams:\n{str_open_teams}\n  Invite a friend by entering the team number and your friend's phone number, separated by a comma. (Type 'menu' to go back)"""
    inbound_format = parsers.ADD_MEMBER

    @classmethod
    def run_actions(self, user, inbound, **kwargs):
        result = multiplayer.insert_member(user, inbound, InitOnboardingInvited, YouWereInvited)
        return {multiplayer.insert_member.__name__ : result}
    
    @classmethod
    def next_router(self, **kwargs):
        return AddMemberConfirmed


class AddMemberConfirmed(BaseRouter):
    outbound = "Sent an invitation to your friend. I'll let you know when they respond."


class InitOnboardingInvited(BaseRouter):
    pre_actions = (multiplayer.get_last_invitation, multiplayer.str_members_of_invited_team)
    outbound = Outbounds.INIT_ONBOARDING_INVITATION
    inbound_format = parsers.MULTIPLE_CHOICE

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'a':
            return EnterUsername
        elif inbound == 'b':
            return GoodbyeFeedback
        elif inbound == 'c':
            return HowItWorks
        elif inbound == 'd':
            return WhoIsUsername
    
    @classmethod
    def run_actions(self, user, inbound, **kwargs):
        membership = multiplayer.respond_to_invite(user, inbound)
        notify_result = multiplayer.notify_inviter(user, membership)
        
        return {multiplayer.respond_to_invite.__name__ : membership,
            multiplayer.notify_inviter.__name__ : notify_result}


class WhoIsUsername(BaseRouter):
    pre_actions = (multiplayer.get_phonenumber,)
    outbound = "Your friend's number is {get_phonenumber}. Hope that helps you identify them. Go back to invitation? (y/n)"
    inbound_format = parsers.YES_NO

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return InitOnboardingInvited
        else:
            return GoodbyeFeedback


class YouWereInvited(BaseRouter):
    pre_actions = (multiplayer.get_last_invitation, multiplayer.str_members_of_invited_team)
    outbound = Outbounds.YOU_WERE_INVITED
    inbound_format = parsers.YES_NO

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return YouJoinedTeam
        else:
            return MainMenu

    @classmethod
    def run_actions(self, user, inbound, **kwargs):
        membership = multiplayer.respond_to_invite(user, inbound)
        notify_result = multiplayer.notify_inviter(user, membership)
        
        return {multiplayer.respond_to_invite.__name__ : membership,
            multiplayer.notify_inviter.__name__ : notify_result}


class YouJoinedTeam(BaseRouter):
    outbound = "Welcome! With your addition, this team has grown in strength."


class ViewTeamMembers(BaseRouter):
    pre_actions = (multiplayer.str_all_teams,)
    outbound = "{str_all_teams}"


class LeaveTeam(BaseRouter):
    pre_actions = (multiplayer.list_teams,)
    outbound = "Your teams:\n{list_teams}\nPlease enter the team number that you want to leave."
    inbound_format = parsers.INTEGER
    actions = (multiplayer.leave_team,)
    confirmation = "Team left."


class WeekReflection(BaseRouter):
    pre_actions = (solo.str_past_tasks,)
    outbound = "Your tasks this past week:{str_past_tasks}\n\n What enabled you to be productive this past week?"
    
    @classmethod
    def next_router(self, **kwargs):
        return WeekReflectionPart2


class WeekReflectionPart2(BaseRouter):
    outbound = "And what hindered your productivity?"
    participation_points = Points.TASK_COMPLETED

    @classmethod
    def next_router(self, **kwargs):
        return WeekReflectionPart3


class WeekReflectionPart3(BaseRouter):
    outbound = "Thanks for reflecting!"


class TeamLeaderboard(BaseRouter):
    pre_actions = (multiplayer.get_team_leaderboard,)
    outbound = "{get_team_leaderboard}"

    @classmethod
    def next_router(self, **kwargs):
        return LeaderboardMenu


class TrapDoor(BaseRouter):
    outbound = "Sorry, this feature doesn't exist yet. If you really want it, text Nico at 312-450-5311"