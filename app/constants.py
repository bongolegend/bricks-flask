class Outbounds:
    HOW_IT_WORKS = """How this works: every weekday, you input your most important task of the day. At the end of the day, you confirm that you did it.
If you did, then you get +X points. If you are consistent, you get extra points. You also get points just for participating. Makes sense? (y/n)"""

    WHAT_TIMEZONE = """What's your timezone?
a) PT
b) MT
c) CT
d) ET
"""

    MAIN_MENU = """What do you want to do?
a) choose a task
b) change timezone
c) help
d) my points
e) leaderboard
f) create a team
g) invite a friend to team
"""


class Points:
    DEFAULT = 0
    TASK_COMPLETED = 10
    CHOOSE_TASK = 1
    DID_YOU_DO_IT = 1
    EARNED_MESSAGE = "+{points} pt earned!"
    ALREADY_EARNED_MESSAGE = "+0 pt (already earned for today)."


class Statuses:
    PENDING = 'pending'
    ACTIVE = 'active'
    REJECTED = 'rejected'
    CONFIRMED = 'confirmed'


US_TIMEZONES = {
    'a': 'America/Los_Angeles',
    'b': 'America/Denver',
    'c': 'America/Chicago',
    'd': 'America/New_York',
}