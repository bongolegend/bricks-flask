import pandas as pd


HOW_IT_WORKS = """How this works: every weekday, you input your most important task of the day. At the end of the day, you confirm that you did it.
If you did, then you get a point. If you are consistent, you get extra points. Makes sense? (y/n)"""

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
d) how many points do I have?
"""

NODES = [
    {
        'router_id': 'init_onboarding',
        'outbound': None,
        'actions': None,
        'inbound_format': '*',
    }, {
        'router_id': 'welcome',
        'outbound': "Hey! Welcome to Bricks, a tool that helps you get stuff done. Please enter a username:",
        'actions': ('update_username',),
        'inbound_format': '*',
        'confirmation': "Your username is set.",
    }, {
        'router_id': 'how_it_works',
        'outbound': HOW_IT_WORKS, 
        'actions': None,
        'inbound_format': 'yes_no',
    }, {
        'router_id': 'contact_support',
        'outbound': "Text me at 3124505311 and I'll walk you through it. Type anything to continue.", 
        'actions': None,
        'inbound_format': '*',
    }, {
        'router_id': 'timezone',
        'outbound': TIMEZONE, 
        'actions': ('update_timezone',), # these get executed in order
        'inbound_format': 'multiple_choice',
        'confirmation': "Your timezone is set.",
    }, {
        'router_id': 'choose_brick', 
        'outbound': "What's the most important thing you want to get done today?",
        'actions': ('schedule_reminders',),
        'inbound_format': '*',
    }, {
        'router_id': 'choose_tomorrow_brick', 
        'outbound': "What's the most important thing you want to get done tomorrow?",
        'actions': ('change_morning_notification',), 
        'inbound_format': '*',
    }, {
        'router_id': 'state_night_followup',
        'outbound': "I'll text you tonight at 9 pm to follow up. Good luck.",
        'actions': None, 
        'inbound_format': '*',
    }, {
        'router_id': 'evening_checkin',
        'outbound': 'Did you stack your brick today? (y/n)',
        'actions': ('add_point',),
        'inbound_format': 'yes_no',
    }, {
        'router_id': 'completion_point',
        'pre_actions': ('query_points',),
        'outbound': "Congrats! You earned +1 point. You now have {query_points} points. Do you want to choose tomorrow's task now? (y/n)",
        'actions': None,
        'inbound_format': 'yes_no',
    }, {
        'router_id': 'no_completion',
        'outbound': "All good. Just make tomorrow count. You currently have {query_points} points. Do you want to choose tomorrow's task now? (y/n)",
        'actions': None,
        'inbound_format': 'yes_no',
    }, {
        'router_id': 'main_menu',
        'outbound': MAIN_MENU,
        'actions': None,
        'inbound_format': 'multiple_choice',
    }, {
        'router_id': 'current_points',
        'pre_actions': ('query_points',),
        'outbound': "You currently have {query_points} points.",
        'actions': None,
        'inbound_format': '*',
    }, {
        'router_id': 'state_morning_followup',
        'outbound': "I'll message you tomorrow at 8 am.",
        'inbound_format': '*',
    }, {
        'router_id': 'morning_confirmation',
        'pre_actions': ('query_brick','change_morning_notification'),
        'outbound': "Are you still planning to do this task today: {query_brick}? (y/n)",
        'inbound_format': 'yes_no',
        'actions': None,
    },
]

nodes = pd.DataFrame.from_dict(NODES)
# pandas reads None as Nan by default, so you need to replace the Nans
nodes = nodes.where((pd.notnull(nodes)), None)


EDGES = [
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
        'last_router_id': 'contact_support',
        'inbound': '*',
        'condition': ('timezone_set', False),
        'next_router_id': 'timezone',
    }, {
        'last_router_id': 'contact_support',
        'inbound': '*',
        'condition': ('timezone_set', True),
        'next_router_id': 'main_menu',
    }, {
        'last_router_id': 'how_it_works',
        'inbound': 'yes',
        'condition': ('timezone_set', False),
        'next_router_id': 'timezone',
    }, {
        'last_router_id': 'how_it_works',
        'inbound': 'yes',
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
        'next_router_id': 'state_night_followup',
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
    }, {
        'last_router_id': 'main_menu',
        'inbound': 'd',
        'next_router_id': 'current_points',
    }, {
        'last_router_id': 'evening_checkin',
        'inbound': 'yes',
        'next_router_id': 'completion_point',
    }, {
        'last_router_id': 'evening_checkin',
        'inbound': 'no',
        'next_router_id': 'no_completion',
    }, {
        'last_router_id': 'current_points',
        'inbound': '*',
        'next_router_id': 'main_menu',
    }, {
        'last_router_id': 'state_night_followup',
        'inbound': '*',
        'next_router_id': 'main_menu',
    }, {
        'last_router_id': 'completion_point', 
        'inbound': 'yes',
        'next_router_id': 'choose_tomorrow_brick',
    }, {
        'last_router_id': 'completion_point', 
        'inbound': 'no',
        'next_router_id': 'state_morning_followup',
    }, {
        'last_router_id': 'no_completion', 
        'inbound': 'yes',
        'next_router_id': 'choose_tomorrow_brick',
    }, {
        'last_router_id': 'no_completion', 
        'inbound': 'no',
        'next_router_id': 'state_morning_followup',
    }, {
        'last_router_id': 'choose_tomorrow_brick', 
        'inbound': '*',
        'next_router_id': 'state_morning_followup',
    }, {
        'last_router_id': 'morning_confirmation',
        'inbound': 'yes',
        'next_router_id': 'state_night_followup',
    }, {
        'last_router_id': 'morning_confirmation',
        'inbound': 'no',
        'next_router_id': 'choose_brick',
    }
]

edges = pd.DataFrame.from_dict(EDGES)
# pandas reads None as Nan by default, so you need to replace the Nans
edges = edges.where((pd.notnull(edges)), None)

routers = nodes.merge(
    edges,
    how='outer',
    left_on='router_id',
    right_on='next_router_id')

routers.drop(['next_router_id'], axis=1, inplace=True)

