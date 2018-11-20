'''This module runs notifications, ie SMS that get sent at 8 am and 10 pm daily'''
import os
import logging
import settings
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
# inspiration: https://github.com/agronholm/apscheduler/blob/master/examples/schedulers/background.py
from notification_db import notifications_df


# use twilio api to send a message
# get the phone number from env for now
def notify(to_number, output):
    '''send output to user with twilio'''

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')

    client = Client(account_sid, auth_token)

    client.messages.create(from_=os.environ.get('TWILIO_PHONE_NUMBER'),
                        to=to_number,
                        body=output)


def schedule_notifications(scheduler, user_number):
    '''add notifications to scheduler for a given user based on db'''

    # filter stored notifications for this user
    user_notifications = notifications_df[notifications_df.to_number == user_number]
   
    def add_job_to_scheduler(row):
        scheduler.add_job(notify, 
            row.trigger_type,
            args=[row.to_number, row.output], # passed to notify func
            **row.kwargs)
    
    user_notifications.apply(add_job_to_scheduler, axis=1)


def main():
    # enable daemonic mode to terminate scheduler when app terminates
    scheduler = BackgroundScheduler(daemon=True)
    schedule_notifications(scheduler, os.environ.get('TEST_PHONE_NUMBER'))
    scheduler.start()

    while True:
        pass


if __name__ == '__main__':
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(message)s')
    logger.setLevel(logging.INFO)
    main()