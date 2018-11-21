'''This module runs notifications, ie SMS that get sent at 8 am and 10 pm daily'''
import os
import logging
import settings
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
# inspiration: https://github.com/agronholm/apscheduler/blob/master/examples/schedulers/background.py
from app.notification_db import notifications_df
from app.models import User, Notification
from config import Config


def main(scheduler=None, test=False):
    '''scheduler starts on a separate thread (initialized in __init__). seed it with stored notifications'''
    # enable daemonic mode to terminate scheduler when app terminates
    if scheduler is None:
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.start()

    seed_scheduler(scheduler) 

    # this is an easy way to send notifications without running the whole app
    if test:
        while True:
            pass
    else:
        return scheduler


def seed_scheduler(scheduler):
    '''get stored notifications from db and add to scheduler'''
   
    # TODO(Nico) this will probably not be implemented as a pandas df
    # add every notif in db to scheduler
    def add_job_to_scheduler(row):
        scheduler.add_job(notify, 
            row.trigger_type,
            args=[row.to_number, row.outbound], # `args` are passed to notify func
            **row.kwargs)
    
    notifications_df.apply(add_job_to_scheduler, axis=1)


def notify(to_number, outbound):
    '''send outbound to user with twilio'''

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    client = Client(account_sid, auth_token)

    client.messages.create(from_=os.environ.get('TWILIO_PHONE_NUMBER'),
                        to=to_number,
                        body=outbound)


def add_notif_to_scheduler(scheduler, notif, user):
    # convert notif to dict
    notif_dict = {key: val for key, val in notif.__dict__.items() if key in CRON_KEYS}
    
    scheduler.add_job(notify,
        notif.trigger_type,
        args=[user.phone_number, notif.body],
        **notif_dict)
    


if __name__ == '__main__':
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(message)s')
    logger.setLevel(logging.INFO)
    main(test=True)
    