import datetime as dt
from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse
from response_db import first_contact_df
from models import User, Notification
from run import db, scheduler
from send_notifications import add_notif_to_scheduler

def main():
    """Respond to input with appropriate output based on conversation state and response_db.py"""

    user = query_or_insert_user(request.values.get('From'))

    # get values from session storage
    counter = session.get('counter', 0)
    last_output = session.get('last_output', None)
    last_output_id = session.get('last_output_id', None)

    # process input
    input = request.values.get('Body')
    print('USER INPUT: ', input,' - ', type(input))

    # decide on output
    output, output_id = choose_output(last_output_id, input, first_contact_df)

    resp = MessagingResponse() # initialize twilio's response tool. it works under the hood
    resp.message(output)

    if output_id == 2 and len(Notification.query.filter_by(user=user, tag='checkin').all()) == 0:
            # set a notification for tonight, recurring
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
            add_notif_to_scheduler(scheduler, notif, user)
            db.session.add(notif)
            db.session.commit()
            

        # TODO(Nico) set a notification for tomorrow morning, recurring

    # save new values to session
    counter += 1
    session['counter'] = counter
    session['last_output'] = output
    session['last_output_id'] = output_id

    return str(resp)


def choose_output(last_output_id, input, first_contact_df):
    responses = first_contact_df.copy()
    
    # check last_output_id matches
    if last_output_id is not None:
        filtered = responses[responses.last_output_id == last_output_id]
    else:
        filtered = responses[responses.last_output_id.isnull()]

    # check input matches
    if input in filtered.input.values: # ASSUME that each last_output_id, input pair is unique
        filtered = filtered[filtered.input == input]
    else: # if there is no matching key, use Null as the wildcard
        filtered = filtered[filtered.input.isnull()] # if there are no wildcard options for this key, you get an empty df

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
        print(f"user already exists: {user}")
        return user
    else:
        new_user = User(phone_number=phone_number)
        db.session.add(new_user)
        db.session.commit()
        print(f"created new user: {new_user}")
        return new_user

# TODO(Nico) implement this
# def update_user_state(...):

