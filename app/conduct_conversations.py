import datetime as dt
from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse
from app import scheduler, db
from app.init_session import main as init_session
from app.parse_inbound import main as parse_inbound
from app.queries import insert_exchange, update_exchange
from app.routers_and_outbounds import combined_routers
from app.router_actions import ROUTER_ACTIONS
from app.condition_checkers import CONDITION_CHECKERS
from config import Config # TODO(Nico) access the config that has been initialized on the app 


def main():
    """Respond to SMS inbound with appropriate SMS outbound based on conversation state and response_db.py"""

    init_session(session, request)

    # gather relevant data from inbound request
    inbound = request.values.get('Body')
    print(f'INBOUND FROM {session["user"]["username"]}: {inbound}')

    # parse inbound based on match on router_id
    parsed_inbound = parse_inbound(inbound, session['exchange']['router_id'])

    # execute all actions defined on the router
    result_dict = execute_actions(
        session['exchange']['actions'], 
        session['exchange']['router_id'], 
        parsed_inbound, 
        session['user'])

    # decide on next router, including outbound and actions
    next_router = pick_response_and_logic(
        session, 
        parsed_inbound, 
        session['user'])

    print('NEXT ROUTER: \n', next_router)
    
    # update current exchange in DB with inbound and next router
    update_exchange(
        session['exchange']['id'], 
        inbound,
        next_router['router_id'])

    # insert the next router into db as an exchange
    next_exchange = insert_exchange(
        next_router, 
        session['user'])

    # save values to persist in session so that we know how to act on user's response to our outbound
    session['exchange'] = next_exchange

    # send outbound    
    resp = MessagingResponse()
    resp.message(next_router['outbound'])
    return str(resp)


def execute_actions(actions, last_router_id, inbound, user):
    if inbound is not None and actions is not None:
        result_dict = dict()
        for action_name in actions:
            action_func = ROUTER_ACTIONS[action_name]

            result = action_func(
                last_router_id=last_router_id, 
                inbound=inbound, 
                user=user)

            result_dict[action_name] = result

        return result_dict
    return None


def pick_response_and_logic(session, inbound, user):
    '''Query the static router table to find the right outbound message and action'''

    if inbound is None:
        # resend the same router
        RETRY = "Your response is not valid, try again.\n"
        session['exchange']['outbound'] = RETRY + session['exchange']['outbound']

        return session['exchange']

    # handle valid inbound message
    routers = combined_routers.copy()
    # match on last router_id
    routers = routers[routers.last_router_id == session['exchange']['router_id']]
    # match on inbound
    routers = routers[(routers.inbound == inbound) |  (routers.inbound == '*')]
    
    if len(routers) == 1:
        router = routers.iloc[0]
    elif len(routers) == 0:
        # redirect to the main menu
        router = combined_routers[combined_routers.router_id == 'main_menu'].iloc[0]
        router['outbound'] = "Can't interpret that; sending you to the menu.\n" + router['outbound']
    else:
        # match on a condition
        matches = 0
        for i, (checker, expected_value) in enumerate(routers['condition']):
            checker_func = CONDITION_CHECKERS[checker]
            if checker_func(user) == expected_value:
                router = routers.iloc[i]
                matches += 1
        if matches > 1:
            raise NotImplementedError("The routers are ambiguous - too many matches. fix your routers.")
        elif matches == 0:
            raise NotImplementedError("The routers are ambiguous - no match for this condition. fix your routers.")
    
    # append last router's confirmation to next router's outbound
    if  session['exchange']['confirmation'] is not None:
        router['outbound'] = session['exchange']['confirmation'] + " " + router['outbound']

    return router
