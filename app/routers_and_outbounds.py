import pandas as pd


HOW_IT_WORKS = """This is how Bricks works: every weekday, you input your most important task of the day. At the end of the day, you confirm that you did it.
If you did, then you get a point. Makes sense? (y/n)"""

# TODO(Nico) instead ask what city you're in. this makes it better to find their locale for analytics
# all good solutions require API access : https://stackoverflow.com/questions/16505501/get-timezone-from-city-in-python-django
TIMEZONE = """
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
"""

OUTBOUNDS = [
    {
        'router_id': 'welcome',
        'response': "Hey! Welcome to Bricks, a tool that helps you outperform your friends. Please enter a username:",
        'actions': ('update_username',),
    }, {
        'router_id': 'how_it_works',
        'response': HOW_IT_WORKS, 
        'actions': (None,),
    }, {
        'router_id': 'contact_support',
        'response': "Text me at 3124505311 and I'll walk you through it.", 
        'actions': (None,),
    }, {
        'router_id': 'timezone',
        'response': TIMEZONE, 
        'actions': ('update_timezone',), # these get executed in order
    }, {
        'router_id': 'choose_brick', 
        'response': "What’s the most important thing you want to get done today?",
        'actions': ('schedule_reminders',), # TODO(Nico) log this brick
    }, {
        'router_id': 'state_followup',
        'response': "I’ll text you tonight at 9 pm to follow up. Good luck.",
        'actions': (None,), 
    }, {
        'router_id': 'evening_checkin',
        'response': 'Did you stack your brick today?',
        'actions': ('add_point',)
    }, {
        'router_id': 'completion_point',
        'response': "Congrats! You earned +1 point.",
        'actions': (None,),
    }, {
        'router_id': 'no_completion',
        'response': "All good. Just make tomorrow count.",
        'actions': (None,),
    }, {
        'router_id': 'main_menu',
        'response': MAIN_MENU,
        'actions': (None,),
    }, 
]


outbound_df = pd.DataFrame.from_dict(OUTBOUNDS)

ROUTERS = [
    {
        'last_router_id': 'init_onboarding',
        'inbound': '*',
        'next_router_id': 'welcome',
    },{
        'last_router_id': 'welcome',
        'inbound': '*',
        'next_router_id': 'how_it_works',
    }, {
        'last_router_id': 'how_it_works',
        'inbound': 'no',
        'next_router_id': 'contact_support',
    }, {
        'last_router_id': 'how_it_works',
        'inbound': 'yes',
        'condition': ('timezone_set', False),
        'next_router_id': 'timezone',
    }, {
        'last_router_id': 'how_it_works',
        'inbound': '*',
        'condition': ('timezone_set', True),
        'next_router_id': 'main_menu',
    }, {
        'last_router_id': 'timezone',
        'inbound': '*',
        'condition': ('brick_chosen', False),
        'next_router_id': 'choose_brick',
    }, {
        'last_router_id': 'timezone',
        'inbound': '*',
        'condition': ('brick_chosen', True),
        'next_router_id': 'main_menu',
    }, {
        'last_router_id': 'choose_brick',
        'inbound': '*',
        'next_router_id': 'state_followup',
    }, {
        'last_router_id': 'state_followup',
        'inbound': '*',
        'next_router_id': 'main_menu',
    }, {
        'last_router_id': 'main_menu',
        'inbound': 'a',
        'next_router_id': 'choose_brick',
    }, {
        'last_router_id': 'main_menu',
        'inbound': 'b',
        'next_router_id': 'timezone',
    }, {
        'last_router_id': 'main_menu',
        'inbound': 'c',
        'next_router_id': 'how_it_works',
    }
]

router_df = pd.DataFrame.from_dict(ROUTERS)

combined_routers = outbound_df.merge(
    router_df,
    how='outer',
    left_on='router_id',
    right_on='next_router_id')


