import datetime as dt
from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse
from app import scheduler, db
from app.router_table import router_df, ACTIONS
from app.models import User, Notification
from app.send_notifications import add_notif_to_scheduler
from config import Config # TODO(Nico) access the config that has been initialized on the app 


def main():
    """Respond to SMS inbound with appropriate SMS outbound based on conversation state and response_db.py"""

    # identify the user
    user = query_or_insert_user(request.values.get('From'))
    
    # get values from session storage
    # TODO(Nico) how does this work? when does it expire? can it handle multiple users? I don't think so
    last_outbound = session.get('last_outbound', None)
    last_outbound_id = session.get('last_outbound_id', 0)

    # ingest inbound message  
    inbound = request.values.get('Body')
    print('SMS INBOUND: ', user, inbound)

    # decide on outbound message and func calls
    outbound, outbound_id = pick_response_and_logic(last_outbound_id, inbound, user)

    # send outbound    
    resp = MessagingResponse() # initialize twilio's response tool. it works under the hood
    resp.message(outbound)

    # save new values to session
    session['last_outbound'] = outbound
    session['last_outbound_id'] = outbound_id

    return str(resp)


def pick_response_and_logic(last_outbound_id, inbound, user):
    '''Query the static router table to find the right outbound message and action'''
    routers = router_df.copy()
    print("INPUTS", last_outbound_id, inbound, user)
    
    # match on last_outbound_id
    routers = routers[routers.last_outbound_id == last_outbound_id]
    print("LAST OUTBOUND", len(routers))
    # match on inbound
    # TODO(Nico) include a parser of user's inbound messages to standardize them 
    if inbound in routers.inbound.values: # ASSUME that each last_outbound_id, inbound pair is unique
        routers = routers[routers.inbound == inbound]
    else: # by default, return the router that accepts any input
        routers = routers[routers.inbound == '*']

    if len(routers) == 0:
        return "No valid response in our db. Restarting the chat from the beginning.", 0
    elif len(routers) > 1:
        raise NotImplementedError("The routers are ambiguous - too many matches. fix your data.")

    # trigger actions
    for action_name in routers.actions.iloc[0]:
        if action_name is not None:
            action = ACTIONS.get(action_name, None)
            assert action is not None, 'action does not match any key in ACTIONS'
            action(last_outbound_id=last_outbound_id, 
                inbound=inbound, 
                user=user)

    return routers.response.iloc[0], int(routers.index.values[0])


def query_or_insert_user(phone_number):
    '''
    use phone number to find user in db, else add to db
    returns the user object
    '''
    user = User.query.filter_by(phone_number=phone_number).first()

    if user is not None:
        print(f"USER ALREADY EXISTS: {user}")
        return user
    else:
        new_user = User(phone_number=phone_number)
        db.session.add(new_user)
        db.session.commit()
        print(f"CREATING NEW USER: {new_user}")
        return new_user
