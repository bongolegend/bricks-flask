'''This module runs notifications, ie SMS that get sent at 8 am and 10 pm daily'''
import os
import logging
import settings
from twilio.rest import Client
from app import scheduler, db
from app.models import User, Notification
from app.tools import insert_exchange
from config import Config # TODO(Nico) find a cleaner way to access config. with create_app? or current_app?


def seed_scheduler():
    '''scheduler starts on a separate thread (initialized in __init__). seed it with stored notifications'''
    result = db.session.query(Notification, User).join(User).all()

    for row in result:
        notif, user = row
        user = user.to_dict()
        add_notif_to_scheduler(scheduler, notif, user, Config)


def add_notif_to_scheduler(scheduler, notif, user, config):
    '''add notification instance to the running scheduler'''
    cron_dict = notif.to_cron()
    
    scheduler.add_job(notify,
        notif.trigger_type,
        args=[user, notif],
        **cron_dict)


def notify(user, notif):
    '''send outbound to user with twilio'''

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    client = Client(account_sid, auth_token)

    client.messages.create(from_=os.environ.get('TWILIO_PHONE_NUMBER'),
        to=user['phone_number'],
        body=notif.body)
    
    # TODO(Nico) look up the appropriate values for this router
    insert_exchange(notif.tag, user)



