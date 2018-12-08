import os
import datetime as dt
from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse
from app import db
from app.init_session import main as init_session
from app.parse_inbound import main as parse_inbound
from app.queries import insert_exchange, update_exchange
from app.routers import routers
from app.router_actions import ROUTER_ACTIONS
from app.condition_checkers import CONDITION_CHECKERS
from config import Config # TODO(Nico) access the config that has been initialized on the app 


def main():
    """Respond to SMS inbound with appropriate SMS outbound based on conversation state and response_db.py"""
    
    inbound = request.values.get('Body')
    if inbound is None:
        return f"Please use a phone and text {os.environ.get('TWILIO_PHONE_NUMBER')}. This does not work thru the browser."

    init_session(session, request)

    session['exchange']['inbound']  = inbound

    # gather relevant data from inbound request
    session['exchange']['inbound'] = request.values.get('Body')
    print(f"INBOUND FROM {session['user']['username']}: {session['exchange']['inbound']}")

    # parse inbound based on match on router_id
    parsed_inbound = parse_inbound(session['exchange']['inbound'], session['exchange']['router_id'])
    
    if parsed_inbound is not None:
        # execute current exchange actions after getting inbound
        # this needs to run before selecting the next router, as these actions can influence the next router choice
        action_results = execute_actions(
            session['exchange']['actions'], 
            session['user'],
            inbound=parsed_inbound)

        # decide on next router, including outbound and actions
        next_router = select_next_router(
            session, 
            parsed_inbound, 
            session['user'])
    else:
        # resend the same router
        RETRY = "Your response is not valid, try again.\n"
        session['exchange']['outbound'] = RETRY + session['exchange']['outbound']

        next_router = session['exchange']
        action_results = dict()

    
    # run actions for next router before inbound
    pre_action_results = execute_actions(
        next_router['pre_actions'],
        session['user'])

    # combine all action results and add them to next router
    results = {**action_results, **pre_action_results}
    next_router['outbound'] = next_router['outbound'].format(**results)

    # insert the next router into db as an exchange
    next_exchange = insert_exchange(
        next_router, 
        session['user'])

    # update current exchange in DB with inbound and next exchange id
    update_exchange(
        session['exchange'],
        next_exchange)

    # save values to persist in session so that we know how to act on user's response to our outbound
    session['exchange'] = next_exchange

    # send outbound    
    resp = MessagingResponse()
    resp.message(next_exchange['outbound'])
    return str(resp)


def execute_actions(actions, user, inbound=None):
    if actions is not None:
        result_dict = dict()
        for action_name in actions:
            action_func = ROUTER_ACTIONS[action_name]

            result = action_func( 
                inbound=inbound, 
                user=user)
            print('ACTION EXECUTED: ', action_name)

            result_dict[action_name] = result

        return result_dict
    return dict()


def select_next_router(session, inbound, user):
    '''Query the static router table to find the right outbound message and action'''

    # find all routers that can branch from the current router & that interact with the inbound
    filtered = routers[
        (routers.last_router_id == session['exchange']['router_id']) & 
        (
            (routers.inbound == inbound) |  
            (routers.inbound == '*')
    )]
    
    if len(filtered) == 1:
        router = filtered.iloc[0]
    elif len(filtered) == 0:
        # redirect to the main menu
        router = routers[routers.router_id == 'main_menu'].iloc[0]
        router['outbound'] = "Can't interpret that; sending you to the menu.\n" + router['outbound']
    else:
        # match on a condition
        matches = 0
        for i, (checker, expected_value) in enumerate(filtered['condition']):
            checker_func = CONDITION_CHECKERS[checker]
            if checker_func(user) == expected_value:
                router = filtered.iloc[i]
                matches += 1
        if matches > 1:
            raise NotImplementedError("The routers are ambiguous - too many matches. fix your routers.")
        elif matches == 0:
            raise NotImplementedError("The routers are ambiguous - no match for this condition. fix your routers.")
    
    # append last router's confirmation to next router's outbound
    if  session['exchange']['confirmation'] is not None:
        router['outbound'] = session['exchange']['confirmation'] + " " + router['outbound']

    print('NEXT ROUTER: \n', router)
    return router
