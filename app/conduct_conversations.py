import datetime as dt
from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse
from app import scheduler, db
from app.routers_and_outbounds import combined_routers
from app.router_actions import ROUTER_ACTIONS
from app.models import User, Notification, Exchange
from app.tools import insert_exchange, update_exchange, parse_inbound
from app.condition_checkers import CONDITION_CHECKERS
from config import Config # TODO(Nico) access the config that has been initialized on the app 


def main():
    """Respond to SMS inbound with appropriate SMS outbound based on conversation state and response_db.py"""

    # identify the user and start the session
    if 'user' not in session:
        session['user'] = query_or_insert_user(request.values.get('From')).to_dict()
        print('\n')
        print(f'SESSION STARTED FOR {session["user"]["username"]}')

    if 'exchange' not in session:
        last_exchange = query_last_exchange(session['user'])

        if last_exchange is not None: # handles returning users
            session['exchange'] = last_exchange
            if session['exchange']['actions'] is None:
                session['exchange']['actions'] = tuple()

            print('LAST EXCHANGE WAS ', session['exchange']['router_id'])
        else: # initiate new exchange
            session['exchange'] = dict()
            session['exchange']['router_id'] = 'init_onboarding'
            session['exchange']['actions'] = tuple()
            session['exchange']['id'] = None
            session['exchange']['confirmation'] = None

    # gather relevant data from inbound request
    inbound = request.values.get('Body')
    print(f'INBOUND FROM {session["user"]["username"]}: {inbound}')

    # parse inbound based on match on router_id
    parsed_inbound = parse_inbound(inbound, session['exchange']['router_id'])

    # execute actions that were defined by the router for this inbound value
    # TODO(Nico) capture returned values of these actions
    execute_actions(
        session['exchange']['actions'], 
        session['exchange']['router_id'], 
        parsed_inbound, 
        session['user'])

    # decide on outbound message and func calls
    next_router = pick_response_and_logic(
        session['exchange']['router_id'], 
        parsed_inbound, 
        session['user'])

    print('THE NEXT ROUTER LOOKS LIKE: \n\n', next_router)
    # update the last exchange
    if session['exchange']['router_id'] != 'init_onboarding':
        update_exchange(
            session['exchange']['id'], 
            inbound,
            next_router.router_id)
    
    # append last router's confirmation to next router's outbound
    if  session['exchange']['confirmation'] is not None:
        next_router.outbound = session['exchange']['confirmation'] + " " + next_router.outbound

    # insert the next exchange
    next_exchange = insert_exchange(
        next_router.router_id, 
        session['user'])

    # save values to persist in session so that we know how to act on user's response to our outbound
    session['exchange'] = next_exchange

    print(f'NEXT ROUTER TO {session["user"]["username"]}: {session["exchange"]["router_id"]}')
    print(f'OUTBOUND TO {session["user"]["username"]}: {session["exchange"]["outbound"]}')

    # send outbound    
    resp = MessagingResponse()
    resp.message(next_router.outbound)
    return str(resp)


def pick_response_and_logic(last_router_id, inbound, user):
    '''Query the static router table to find the right outbound message and action'''
    routers = combined_routers.copy()

    # match on last router_id
    routers = routers[routers.last_router_id == last_router_id]
    # match on inbound
    routers = routers[(routers.inbound == inbound) |  (routers.inbound == '*')]
    
    if len(routers) == 1:
        router = routers.iloc[0]
    elif len(routers) == 0:
        # redirect to the main menu
        router = combined_routers[combined_routers.router_id == 'main_menu'].iloc[0]
        router.response = "Can't interpret that; sending you to the menu. " + router.response
    else:
        # match on condition
        matches = 0
        for i, (checker, expected_value) in enumerate(routers.condition):
            if CONDITION_CHECKERS[checker](user) == expected_value:
                router = routers.iloc[i]
                matches += 1
        if matches > 1:
            raise NotImplementedError("The routers are ambiguous - too many matches. fix your routers.")

    return router


def query_or_insert_user(phone_number):
    '''
    use phone number to find user in db, else add to db
    returns the user object
    '''
    user = User.query.filter_by(phone_number=phone_number).first()

    if user is not None:
        return user
    else:
        new_user = User(phone_number=phone_number)
        db.session.add(new_user)
        db.session.commit()
        return new_user


def query_last_exchange(user):
    '''find the last exchange in the db for this user'''
    last_exchange = db.session.query(Exchange)\
        .filter_by(user_id=user['id'])\
        .order_by(Exchange.created.desc())\
        .first()
    
    if last_exchange is None:
        return None
    else:
        return last_exchange.to_dict()


def execute_actions(actions, last_router_id, inbound, user):
    for action_name in actions:
        if action_name is not None:
            action = ROUTER_ACTIONS.get(action_name, None)
            assert action is not None, 'action does not match any key in ROUTER_ACTIONS'
            action(last_router_id=last_router_id, 
                inbound=inbound, 
                user=user)
    
    # TODO(Nico) some of these actions may return values that we want to send to user


'''
    if session exists
        use all the session stuff

        lets just make it work assuming the session is always live
''' 