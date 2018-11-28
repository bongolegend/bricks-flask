""""this is a dummy db implemented with a Pandas dataframe"""
import pandas as pd
from app import actions 


HOW_IT_WORKS = "It is pure magic"

WELCOME = """
Hey! Welcome to Bricks, a tool that helps you outperform your friends. Respond with the number of what you want to do:
a) choose my first brick
b) how does this work?
"""

# TODO(Nico) instead ask what city you're in. this makes it better to find their locale for analytics
# all good solutions require API access : https://stackoverflow.com/questions/16505501/get-timezone-from-city-in-python-django
TZ_QUESTION = """
What's your timezone?
a) PT
b) MT
c) CT
d) ET
"""

ROUTERS = {
    1: [
        0,
        '*',
        WELCOME,
        (None,)        
    ],
    2: [
        1,
        'a',
        "Ok, so what’s the most important thing you want to get done today?",
        (None,)
    ],
    3: [
        2,
        '*',
        f"gotcha. {TZ_QUESTION}",
        (None,)
    ],
    4: [
        1,
        'b',
        HOW_IT_WORKS,
        (None,)
    ],
    5: [
        3,
        '*',
        "I’ll text you tonight at 9 pm to follow up and make sure you did that.",
        ('update_timezone','schedule_reminders' ) # these get executed in order
    ]
}

router_df = pd.DataFrame.from_dict(ROUTERS, 
    orient='index',
    columns=['last_outbound_id', 'inbound', 'response', 'actions']
)

ACTIONS = {
    'schedule_reminders': actions.schedule_reminders,
    'update_timezone': actions.update_timezone
}