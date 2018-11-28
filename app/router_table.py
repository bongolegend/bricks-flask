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

ROUTERS = [
    {
        'router_id': 1,
        'last_router_id': 0, 
        'inbound': '*', 
        'response': WELCOME, 
        'actions': (None,)
    }, {
        'router_id': 2,
        'last_router_id': 1, 
        'inbound': 'a', 
        'response': "Ok, so what’s the most important thing you want to get done today?", 
        'actions': (None,)
    }, {
        'router_id': 3,
        'last_router_id': 2, 
        'inbound': '*', 
        'response': f"gotcha. {TZ_QUESTION}", 
        'actions': (None,)
    }, {
        'router_id': 4,
        'last_router_id': 1, 
        'inbound': 'b', 
        'response': HOW_IT_WORKS, 
        'actions': (None,)
    }, {
        'router_id': 5,
        'last_router_id': 3, 
        'inbound': '*', 
        'response': "I’ll text you tonight at 9 pm to follow up and make sure you did that.", 
        'actions': ('update_timezone','schedule_reminders' ) # these get executed in order
    }
]

router_df = pd.DataFrame.from_dict(ROUTERS)

ACTIONS = {
    'schedule_reminders': actions.schedule_reminders,
    'update_timezone': actions.update_timezone
}