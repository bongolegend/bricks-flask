class Outbounds:
    HOW_IT_WORKS = """Instructions: every day, enter your most important task. At the end of the day, if you complete your task, you get +10 points. If you stay consistent, you get bonuses that double your points. Does this make sense? (y/n)"""

    WHAT_TIMEZONE = """What's your timezone?
a) PT
b) MT
c) CT
d) ET
"""

    MAIN_MENU = """MAIN MENU
{get_username}: {get_total_points}pts

What do you want to do?
a) choose a task
b) invite a friend
c) create a team
d) view team members
e) view leaderboard
f) PROFILE MENU
"""

    RETRY = "Your response is not valid, try again.\n"

    PROFILE_MENU = """PROFILE MENU
What do you want to do?
a) change timezone
b) change username
c) help
d) MAIN MENU"""

    INIT_ONBOARDING_INVITATION = """
Hey! Your friend {get_last_invitation[0]} invited you to join their team {get_last_invitation[1]}, on the Bricks app. 
a) Accept
b) Decline
c) What is this?
d) Who is {get_last_invitation[0]}?
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