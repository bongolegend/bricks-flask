import datetime as dt
from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse
from app import scheduler, db
from app.router_table import router_df, ROUTER_ACTIONS
from app.models import User, Notification, Exchange
from app.tools import log_convo
from config import Config # TODO(Nico) access the config that has been initialized on the app 


def main():
    """Respond to SMS inbound with appropriate SMS outbound based on conversation state and response_db.py"""

    # identify the user and start the session
    if 'user' not in session:
        session['user'] = user = query_or_insert_user(request.values.get('From')).to_dict()
        print(f'SESSION STARTED FOR {user["username"]}')

        last_exchange = query_last_exchange(user)
        if last_exchange is not None: # handles returning users
            session['last_router_id'] = last_exchange
            print('LAST EXCHANGE WAS ', session['last_router_id'])
    else: # handle session that is active
        user = session.get('user')

    last_router_id = session.get('last_router_id', 'init_onboarding')

    # ingest inbound message  
    inbound = request.values.get('Body')

    # decide on outbound message and func calls
    print(f'INBOUND FROM {user["username"]}: {inbound}')
    outbound, router_id = pick_response_and_logic(last_router_id, inbound, user)
    print(f'OUTBOUND TO {user["username"]}: {outbound}')

    # send outbound    
    resp = MessagingResponse() # initialize twilio's response tool. it works under the hood
    resp.message(outbound)

    # save new values to session
    session['last_router_id'] = router_id
    session['user'] = user

    # log convo to db
    log_convo(router_id, inbound, outbound, user)

    return str(resp)


def pick_response_and_logic(last_router_id, inbound, user):
    '''Query the static router table to find the right outbound message and action'''
    routers = router_df.copy()
    
    # match on last_router_id
    routers = routers[routers.last_router_id == last_router_id]
    # match on inbound
    # TODO(Nico) include a parser of user's inbound messages to standardize them 
    if inbound in routers.inbound.values: # ASSUME that each last_router_id, inbound pair is unique
        routers = routers[routers.inbound == inbound]
    else: # by default, return the router that accepts any input
        routers = routers[routers.inbound == '*']

    if len(routers) == 0:
        return "No valid response in our db. Restarting the chat from the beginning.", 'init_onboarding'
    elif len(routers) > 1:
        raise NotImplementedError("The routers are ambiguous - too many matches. fix your data.")

    router = routers.iloc[0]

    # trigger actions
    for action_name in router.actions:
        if action_name is not None:
            action = ROUTER_ACTIONS.get(action_name, None)
            assert action is not None, 'action does not match any key in ROUTER_ACTIONS'
            action(last_router_id=last_router_id, 
                inbound=inbound, 
                user=user)

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
        return last_exchange.router_id
