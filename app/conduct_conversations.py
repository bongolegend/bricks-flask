import datetime as dt
from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse
from app import scheduler, db
from app.phrase_db import first_contact_df
from app.models import User, Notification
from app.send_notifications import add_notif_to_scheduler
from config import Config # TODO(Nico) find a cleaner way to access config. with create_app? or current_app?


def main():
    """Respond to SMS inbound with appropriate SMS outbound based on conversation state and response_db.py"""

    user = query_or_insert_user(request.values.get('From'))

    # get values from session storage
    counter = session.get('counter', 0)
    last_outbound = session.get('last_outbound', None)
    last_outbound_id = session.get('last_outbound_id', None)

    # process inbound
    inbound = request.values.get('Body')
    print('USER SMS INBOUND: ', inbound,' - ', type(inbound))

    # decide on outbound
    outbound, outbound_id = choose_phrase(last_outbound_id, inbound, first_contact_df)

    resp = MessagingResponse() # initialize twilio's response tool. it works under the hood
    resp.message(outbound)

    ############
    ### set notifications to scheduler as appropriate

    # set a recurring notification for tonight - as long as it doesnt already exist
    if outbound_id == 2 and len(Notification.query.filter_by(user=user, tag='checkin').all()) == 0:
            
            notif = Notification(tag='checkin',
                body="DID you stack your brick today?",
                trigger_type='cron',
                day_of_week='mon-fri',
                hour=21,
                minute=55,
                jitter=0,
                end_date=dt.datetime(2018,11,30),
                timezone='America/Denver',
                user=user)
            
            # TODO(Nico) it could be problematic to schedule this before committing to db
            add_notif_to_scheduler(scheduler, notif, user.phone_number, Config)
            db.session.add(notif)
            db.session.commit()
            

    # TODO(Nico) set a notification for tomorrow morning, recurring

    # save new values to session
    counter += 1
    session['counter'] = counter
    session['last_outbound'] = outbound
    session['last_outbound_id'] = outbound_id

    return str(resp)


def choose_phrase(last_outbound_id, inbound, first_contact_df):
    phrases = first_contact_df.copy()
    
    # check last_outbound_id matches
    if last_outbound_id is not None:
        filtered = phrases[phrases.last_outbound_id == last_outbound_id]
    else:
        filtered = phrases[phrases.last_outbound_id.isnull()]

    # check inbound matches
    if inbound in filtered.inbound.values: # ASSUME that each last_outbound_id, inbound pair is unique
        filtered = filtered[filtered.inbound == inbound]
    else: # if there is no matching key, use Null as the wildcard
        filtered = filtered[filtered.inbound.isnull()] # if there are no wildcard options for this key, you get an empty df

    if len(filtered) == 0:
        return "No valid response in our db. Restarting the chat from the beginning.", None

    return filtered.response.iloc[0], int(filtered.index.values[0])


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

