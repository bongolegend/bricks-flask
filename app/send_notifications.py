'''This module runs notifications, ie SMS that get sent at 8 am and 10 pm daily'''
import os
import datetime as dt
import pytz
import logging
import settings
from twilio.rest import Client
from app import db
from app.models import AppUser, Notification
from app.queries import insert_exchange
from app.routers import nodes
from config import Config # TODO(Nico) find a cleaner way to access config. with create_app? or current_app?


def main():
    '''get notifications from db and run the appropriate ones'''

    result = db.session.query(Notification, AppUser).join(AppUser).all()
    print(f"{len(result)} notifications found in db.")
    # look at each time, and check if it's the right time
    # TODO(Nico) think of a better way to optimize this

    margin = dt.timedelta(minutes=10)
    utc_time = dt.datetime.now(tz=pytz.utc)
    earliest_time = utc_time - margin
    latest_time = utc_time + margin
    counter = 0
    for (notif, user) in result:
        user = user.to_dict()
        notif = notif.to_dict()

        notif_tz = pytz.timezone(notif['timezone'])
        local_time = dt.datetime.now(notif_tz)
        # assume that every notif gets sent every day
        reminder_local_time = dt.datetime(
            local_time.year, 
            local_time.month, 
            local_time.day, 
            notif['hour'], # hour and minute are saved in db as local time
            notif['minute'], 
            tzinfo=notif_tz)

        reminder_utc_time = reminder_local_time.astimezone(pytz.utc)

        if earliest_time <= reminder_utc_time <= latest_time:
            notify(user, notif)
            counter += 1
    
    response = f"{counter} of {len(result)} notifications were sent."
    print(response)

    return response





# def seed_scheduler():
#     '''scheduler starts on a separate thread (initialized in __init__). seed it with stored notifications'''
#     result = db.session.query(Notification, AppUser).join(AppUser).all()

#     for row in result:
#         notif, user = row
#         user = user.to_dict()
#         add_notif_to_scheduler(scheduler, notif, user, Config)


# def add_notif_to_scheduler(scheduler, notif, user, config):
#     '''add notification instance to the running scheduler'''
#     cron_dict = notif.to_cron()
    
#     scheduler.add_job(notify,
#         notif.trigger_type,
#         args=[user, notif],
#         **cron_dict)


def notify(user, notif):
    '''send outbound to user with twilio'''

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    client = Client(account_sid, auth_token)

    client.messages.create(from_=os.environ.get('TWILIO_PHONE_NUMBER'),
        to=user['phone_number'],
        body=notif['body'])
    
    node = nodes[nodes.router_id == notif['tag']].iloc[0]

    insert_exchange(node, user)



