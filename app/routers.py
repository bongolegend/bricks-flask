import app.router_actions as actions
from app import parsers
import app.conditions as conditions


HOW_IT_WORKS = """How this works: every weekday, you input your most important task of the day. At the end of the day, you confirm that you did it.
If you did, then you get a point. If you are consistent, you get extra points. Makes sense? (y/n)"""

# TODO(Nico) instead ask what city you're in. this makes it better to find their locale for analytics
# all good solutions require API access : https://stackoverflow.com/questions/16505501/get-timezone-from-city-in-python-django
WHAT_TIMEZONE = """
What's your timezone?
a) PT
b) MT
c) CT
d) ET
"""

MAIN_MENU = """
What do you want to do?
a) choose a brick for today
b) choose a new timezone
c) how does this work?
d) how many points do I have?
"""


class Router:
    pre_actions = None
    actions = None
    inbound_format = parsers.ANY
    confirmation = None

    @classmethod
    def next_router(self, **kwargs):
        return MainMenu
    
    @classmethod
    def parse(self, inbound, **kwargs):
        return parsers.parse(inbound, self.inbound_format)


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
    outbound = HOW_IT_WORKS
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
    outbound = MAIN_MENU
    inbound_format = parsers.MULTIPLE_CHOICE

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'a':
            return ChooseTask
        elif inbound == 'b':
            return Timezone
        elif inbound == 'c':
            return HowItWorks
        elif inbound == 'd':
            return CurrentPoints


class Timezone(Router):
    name = 'timezone'
    outbound = WHAT_TIMEZONE
    actions = (actions.update_timezone,)
    inbound_format = parsers.MULTIPLE_CHOICE
    confirmation = "Your timezone is set."

    @classmethod
    def next_router(self, user, **kwargs):
        if conditions.task_chosen(user):
            return MainMenu
        else:
            return ChooseTask


class ChooseTask(Router):
    name = 'choose_task'
    outbound = "What's the most important thing you want to get done today?"
    actions = (actions.insert_notifications, actions.insert_task)
 
    @classmethod   
    def next_router(self, **kwargs):
        return StateNightFollowup


class CurrentPoints(Router):
    name = 'current_points'
    pre_actions = (actions.query_points,)
    outbound = "You currently have {query_points} points."


class StateNightFollowup(Router):
    name = 'state_night_followup'
    outbound = "I'll text you tonight at 9 pm to follow up. Good luck."


class ChooseTomorrowTask(Router):
    name = 'choose_tomorrow_task'
    outbound = "What's the most important thing you want to get done tomorrow?"
    actions = (actions.change_morning_notification, actions.insert_task)

    @classmethod
    def next_router(self, **kwargs):
        return StateMorningFollowup


class DidYouDoIt(Router):
    name= 'did_you_do_it'
    outbound = 'Did you stack your brick today? (y/n)'
    actions = (actions.add_point,)
    inbound_format = parsers.YES_NO

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
    outbound = "Congrats! You earned +1 point. You now have {query_points} points. Do you want to choose tomorrow's task now? (y/n)",
    inbound_format = parsers.YES_NO

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

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return ChooseTomorrowTask
        elif inbound == 'no':
            return StateMorningFollowup


class StateMorningFollowup(Router):
    name = 'state_morning_followup'
    outbound =  "I'll message you tomorrow at 8 am."


class MorningConfirmation(Router):
    name = 'morning_confirmation'
    pre_actions = (actions.query_task, actions.change_morning_notification)
    outbound = "Are you still planning to do this task today: {query_task}? (y/n)"
    inbound_format = parsers.YES_NO

    @classmethod
    def next_router(self, inbound, **kwargs):
        if inbound == 'yes':
            return StateNightFollowup
        elif inbound == 'no':
            return ChooseTask


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
}