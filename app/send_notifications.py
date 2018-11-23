'''This module runs notifications, ie SMS that get sent at 8 am and 10 pm daily'''
import os
import logging
import settings
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
# inspiration: https://github.com/agronholm/apscheduler/blob/master/examples/schedulers/background.py
from app import scheduler, db
from app.notification_db import notifications_df
from app.models import User, Notification
from config import Config # TODO(Nico) find a cleaner way to access config. with create_app? or current_app?


def seed_scheduler(test=False):
    '''scheduler starts on a separate thread (initialized in __init__). seed it with stored notifications'''
    result = db.session.query(Notification, User).join(User).all()

    for row in result:
        notif, user = row
        add_notif_to_scheduler(scheduler, notif, user.phone_number, Config)

    # this is an easy way to send notifications without running the whole app
    if test:
        while True:
            pass
    else:
        return scheduler


def add_notif_to_scheduler(scheduler, notif, phone_number, config):
    '''add notification instance to the running scheduler'''
    notif_dict = {key: val for key, val in notif.__dict__.items() if key in config.CRON_KEYS}

    # TODO(Nico) you might want to use a persistent job store
    # https://apscheduler.readthedocs.io/en/latest/modules/jobstores/sqlalchemy.html#apscheduler.jobstores.sqlalchemy.SQLAlchemyJobStore
    
    scheduler.add_job(notify,
        notif.trigger_type,
        args=[phone_number, notif.body],
        **notif_dict)


def notify(to_number, outbound):
    '''send outbound to user with twilio'''

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    client = Client(account_sid, auth_token)

    client.messages.create(from_=os.environ.get('TWILIO_PHONE_NUMBER'),
                        to=to_number,
                        body=outbound)

    
if __name__ == '__main__':
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(message)s')
    logger.setLevel(logging.INFO)
    main(test=True)
    