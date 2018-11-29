""""this is a dummy db implemented with a Pandas dataframe"""
import pandas as pd
from app import router_actions 


HOW_IT_WORKS = "It is pure magic"

INTRO_MENU = """
What do you want to do?
a) choose my first brick
b) how does this work?
"""

# TODO(Nico) instead ask what city you're in. this makes it better to find their locale for analytics
# all good solutions require API access : https://stackoverflow.com/questions/16505501/get-timezone-from-city-in-python-django
TIMEZONE = """
What's your timezone?
a) PT
b) MT
c) CT
d) ET
"""

ROUTERS = [
    {
        'router_id': 'welcome',
        'last_router_id': 'init_onboarding',
        'inbound': '*',
        'actions': (None,),
        'response': "Hey! Welcome to Bricks, a tool that helps you outperform your friends. Please enter a username:",
    }, {
        'router_id': 'first_menu',
        'last_router_id': 'welcome', 
        'inbound': '*', 
        'actions': ('update_username',),
        'response': INTRO_MENU, 
    }, {
        'router_id': 'first_brick',
        'last_router_id': 'first_menu', 
        'inbound': 'a',  
        'actions': (None,),
        'response': "Ok, so what’s the most important thing you want to get done today?"
    }, {
        'router_id': 'timezone',
        'last_router_id': 'first_brick', 
        'inbound': '*', 
        'actions': (None,),
        'response': f"gotcha. {TIMEZONE}", 
    }, {
        'router_id': 'first_reminder',
        'last_router_id': 'timezone', 
        'inbound': '*',  
        'actions': ('update_timezone','schedule_reminders' ), # these get executed in order
        'response': "I’ll text you tonight at 9 pm to follow up and make sure you did that.",
    }, {
        'router_id': 'how_it_works',
        'last_router_id': 'first_menu', 
        'inbound': 'b',
        'actions': (None,),
        'response': HOW_IT_WORKS, 
    },
]

router_df = pd.DataFrame.from_dict(ROUTERS)

ROUTER_ACTIONS = {
    'schedule_reminders': router_actions.schedule_reminders,
    'update_timezone': router_actions.update_timezone,
    'update_username': router_actions.update_username
}