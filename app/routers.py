from app import parsers, actions, conditions
from app.constants import Outbounds, Names, Points


class Router:
    pre_actions = None
    actions = None
    inbound_format = parsers.ANY
    confirmation = None
    participation_points = Points.DEFAULT

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
    name = 'init_onboarding'

    @classmethod
    def next_router(self, **kwargs):
        return Welcome


class Welcome(Router):
    name = 'welcome'
    outbound = "Hey! Welcome to Bricks, a tool that helps you get stuff done. Please enter a username:"
    actions = (actions.update_username,)
    confirmation = "Your username is set."

    @classmethod
    def next_router(self, **kwargs):
        return HowItWorks


class HowItWorks(Router):
    name = 'how_it_works'
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
    name = 'contact_support'
    outbound =  "Text me at 3124505311 and I'll walk you through it. Type anything to continue."

    @classmethod
    def next_router(self, user, **kwargs):
        if conditions.timezone_set(user):
            return MainMenu
        else:
            return Timezone


class MainMenu(Router):
    name = 'main_menu'
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


class Timezone(Router):
    name = 'timezone'
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
    name = Names.CHOOSE_TASK
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

        insert_task_result = actions.insert_task(user, 
            exchange, 
            inbound, 
            self, 
            ChooseTomorrowTask)
        
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
    name = 'current_points'
    pre_actions = (actions.query_points,)
    outbound = "You currently have +{query_points} pt."


class StateNightFollowup(Router):
    name = 'state_night_followup'
    outbound = "I'll text you tonight at 9 pm to follow up. Good luck."


class ChooseTomorrowTask(Router):
    name = 'choose_tomorrow_task'
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

        change_result = actions.change_morning_notification(user, ChooseTask, MorningConfirmation)

        insert_result = actions.insert_task(user, exchange, inbound, ChooseTask, ChooseTomorrowTask)

        return {
            actions.insert_notifications.__name__ : insert_notif_result,
            actions.change_morning_notification.__name__ : change_result,
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
    name= Names.DID_YOU_DO_IT
    outbound = 'Did you stack your brick today? (y/n)'
    actions = (actions.insert_points,)
    inbound_format = parsers.YES_NO
    participation_points = Points.DID_YOU_DO_IT

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return CompletionPoint
        elif inbound == 'no':
            return NoCompletion

# TODO combine this with the one below it
class CompletionPoint(Router):
    name = 'completion_point'
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
    name = 'no_completion'
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
    name = 'state_morning_followup'
    outbound =  "Great. I'll message you tomorrow at 8 am to confirm."


class MorningConfirmation(Router):
    name = Names.MORNING_CONFIRMATION
    outbound = "Are you still planning to do this task today: {query_task}? (y/n)"
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
        query_task_result = actions.query_task(user, ChooseTask, ChooseTomorrowTask)

        change_morning_notif_result = actions.change_morning_notification(user, ChooseTask, self)

        return {
            actions.query_task.__name__ : query_task_result,
            actions.change_morning_notification.__name__ : change_morning_notif_result}


class Leaderboard(Router):
    name = 'leaderboard'
    pre_actions = (actions.leaderboard,)
    outbound = "{leaderboard}"


class CreateTeam(Router):
    name = 'create_team'
    outbound = "What do you want to name your team?"
    actions = (actions.insert_team,)
    confirmation = "Team created."
    

routers = {
    InitOnboarding.name : InitOnboarding,
    Welcome.name : Welcome,
    HowItWorks.name : HowItWorks,
    ContactSupport.name : ContactSupport,
    MainMenu.name : MainMenu,
    Timezone.name : Timezone,
    ChooseTask.name : ChooseTask,
    CurrentPoints.name : CurrentPoints,
    StateNightFollowup.name : StateNightFollowup,
    ChooseTomorrowTask.name : ChooseTomorrowTask,
    DidYouDoIt.name : DidYouDoIt,
    CompletionPoint.name : CompletionPoint, 
    NoCompletion.name : NoCompletion,
    StateMorningFollowup.name : StateMorningFollowup,
    Leaderboard.name : Leaderboard,
    CreateTeam.name : CreateTeam,
}