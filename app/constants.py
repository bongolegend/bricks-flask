class Outbounds:
    HOW_IT_WORKS = """
Instructions: every day, enter your most important task. 
At the end of the day, if you complete your task, you get +10 points. 
Does this make sense? (y/n)"""

    WHAT_TIMEZONE = """What's your timezone?
a) PT
b) MT
c) CT
d) ET
"""

    MAIN_MENU = """MAIN MENU
{get_username}: {get_total_points}pts

What do you want to do?
a) Create a task
b) Invite a friend
c) Create a team
d) View team members
e) Leaderboard Menu
f) Settings
"""

    RETRY = "Your response is not valid, try again.\n"

    SETTINGS = """SETTINGS

a) Change timezone
b) Change username
c) Leave team
d) Help
e) Main Menu"""

    LEADERBOARD_MENU = """LEADERBOARDS

a) Team (you vs your team mates)
b) League (your teams vs other teams)
c) Global (you vs all)
d) Main Menu"""

    INIT_ONBOARDING_INVITATION = """
Hey! Your friend {get_last_invitation[0]} invited you to join their team {get_last_invitation[1]}, on Bricks, a productivity chatbot. 
Current team members:{str_members_of_invited_team}

a) Accept
b) Decline
c) What is this?
d) Who is {get_last_invitation[0]}?
"""

    YOU_WERE_INVITED = """
Hey! Your friend {get_last_invitation[0]} invited you to join their team {get_last_invitation[1]}. 
Current team members:{str_members_of_invited_team}
Do you want to accept? (y/n)
"""


class Points:
    DEFAULT = 0
    TASK_COMPLETED = 10
    CHOOSE_TASK = 1
    DID_YOU_DO_IT = 1
    EARNED_MESSAGE = "+{points} pt earned!"
    ALREADY_EARNED_MESSAGE = "+0 pt (already earned for today)."


class Statuses:
    PENDING = 'PENDING'
    ACTIVE = 'ACTIVE'
    REJECTED = 'REJECTED'
    CONFIRMED = 'CONFIRMED'
    LEFT = 'LEFT'


US_TIMEZONES = {
    'a': 'America/Los_Angeles',
    'b': 'America/Denver',
    'c': 'America/Chicago',
    'd': 'America/New_York',
}


class Redirects:
    MAIN_MENU = 'MAIN_MENU'


class Reserved:
    NEW_USER = 'NEW_USER'


class RouterNames:
    CHOOSE_TASK = 'ChooseTask'
    CHOOSE_TOMORROW_TASK = 'ChooseTomorrowTask'
    MORNING_CONFIRMATION = 'MorningConfirmation'
    DID_YOU_DO_IT = 'DidYouDoIt'
    INIT_ONBOARDING_INVITED = 'InitOnboardingInvited'
    WEEK_REFLECTION = 'WeekReflection'


class Sizes:
    INBOUND_MAX_LENGTH = 612

WEEKDAYS = {
    'mon': (0,),
    'tue': (1,),
    'wed': (2,),
    'thur': (3,),
    'fri': (4,),
    'sat': (5,),
    'sun': (6,),
    'mon-fri': (0,1,2,3,4),
    'mon-sat': (0,1,2,3,4,5),
    'daily': (0,1,2,3,4,5,6,),
}

class Push:
    ALGORITHM = "ES256"

class Tasks:
    KEYS = (
        "username",
        "user_id", 
        "member_id",

        "team_name", 
        "team_id", 
        
        "task_id",
        "due_date",
        "description",
        "grade",
        
        "points_earned",
        "points_total"
    )