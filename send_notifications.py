'''This module runs notifications, ie SMS that get sent at 8 am and 10 pm daily'''
import os
import logging
import settings
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
# inspiration: https://github.com/agronholm/apscheduler/blob/master/examples/schedulers/background.py
from notification_db import notifications_df


def main(test=False):
    '''start the scheduler on a separate thread. seed it with stored notifications'''
    # enable daemonic mode to terminate scheduler when app terminates
    scheduler = BackgroundScheduler(daemon=True)
    seed_scheduler(scheduler, os.environ.get('TEST_PHONE_NUMBER'))
    scheduler.start()
    # TODO(Nico) add a listener for new notifications getting added to db

    # this is an easy way to send notifications without running the whole app
    if test:
        while True:
            pass
    else:
        # this allows you to add jobs
        # though the better way to implement might be to seed the db,
        # and start the scheduler back up. That also seems problematic
        # maybe you both seed the db AND add a job to the current thread
        return scheduler


def seed_scheduler(scheduler, user_number):
    '''get stored notifications for a user from db and add to scheduler'''

    # filter stored notifications for this user
    user_notifications = notifications_df[notifications_df.to_number == user_number]
   
    def add_job_to_scheduler(row):
        scheduler.add_job(notify, 
            row.trigger_type,
            args=[row.to_number, row.output], # passed to notify func
            **row.kwargs)
    
    user_notifications.apply(add_job_to_scheduler, axis=1)


def notify(to_number, output):
    '''send output to user with twilio'''

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    client = Client(account_sid, auth_token)

    client.messages.create(from_=os.environ.get('TWILIO_PHONE_NUMBER'),
                        to=to_number,
                        body=output)


if __name__ == '__main__':
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(message)s')
    logger.setLevel(logging.INFO)
    main(test=True)
    