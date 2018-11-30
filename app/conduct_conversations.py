import datetime as dt
from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse
from app import scheduler, db
from app.routers_and_outbounds import combined_routers
from app.router_actions import ROUTER_ACTIONS
from app.models import User, Notification, Exchange
from app.tools import log_convo
from config import Config # TODO(Nico) access the config that has been initialized on the app 


def main():
    """Respond to SMS inbound with appropriate SMS outbound based on conversation state and response_db.py"""

    # identify the user and start the session
    if 'user' not in session:
        user = query_or_insert_user(request.values.get('From')).to_dict()
        print(f'SESSION STARTED FOR {user["username"]}')
        last_exchange = query_last_exchange(user)

        if last_exchange is not None: # handles returning users      
            current_router_id = last_exchange['router_id']
            current_outbound = last_exchange['outbound']    
            current_actions = combined_routers[combined_routers.router_id == last_exchange['router_id']].actions.iloc[0]
            current_exchange_id = last_exchange['id']
            print('LAST EXCHANGE WAS ', current_router_id)
        else:
            current_router_id = 'init_onboarding'
            current_outbound = None
            current_actions = tuple()
            current_exchange_id = None

    else: # handle active session
        user = session['user']
        current_router_id = session['current_router_id']
        current_outbound = session['current_outbound']
        current_actions = session['current_actions']
        current_exchange_id = session['current_exchange_id']

    # gather relevant data from session and inbound
    inbound = request.values.get('Body')
    print(f'INBOUND FROM {user["username"]}: {inbound}')

    # execute actions that were defined by last router for this inbound value
    execute_actions(current_actions, current_router_id, inbound, user)
    
    log_convo(
        current_router_id, 
        inbound, 
        current_outbound, 
        user, 
        exchange_id=current_exchange_id)

    # decide on outbound message and func calls
    next_outbound, next_router_id = pick_response_and_logic(current_router_id, inbound, user)
    print(f'OUTBOUND TO {user["username"]}: {next_outbound}')

    current_exchange_id = log_convo(
        next_router_id, 
        None, 
        next_outbound, 
        user)

    # save values to persist in session so that we know how to act on user's response to our outbound
    session['user'] = user
    session['current_router_id'] = next_router_id
    session['current_outbound'] = next_outbound
    session['current_actions'] = combined_routers[combined_routers.router_id == next_router_id].actions.iloc[0]
    session['current_exchange_id'] = current_exchange_id
    # send outbound    
    resp = MessagingResponse()
    resp.message(next_outbound)
    return str(resp)


def pick_response_and_logic(last_router_id, inbound, user):
    '''Query the static router table to find the right outbound message and action'''
    routers = combined_routers.copy()
    # join the ROUTER and the OUTBOUND tables
    
    # match on last_router_id
    routers = routers[routers.last_router_id == last_router_id]
    # match on inbound
    # TODO(Nico) include a parser of user's inbound messages to standardize them 
    if inbound in routers.inbound.values: # ASSUME that each last_router_id, inbound pair is unique
        routers = routers[routers.inbound == inbound]
    else: # by default, return the router that accepts any input
        routers = routers[routers.inbound == '*']

    if len(routers) == 1:
        router = routers.iloc[0]
    elif len(routers) == 0:
        # redirect to the main menu
        router = combined_routers[combined_routers.router_id == 'main_menu'].iloc[0]
        router.response = "Can't interpret that; sending you to the menu. " + router.response
    else:
        raise NotImplementedError("The routers are ambiguous - too many matches. fix your data.")

    return router.response, router.router_id


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