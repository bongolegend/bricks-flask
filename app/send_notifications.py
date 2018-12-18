'''This module runs notifications, ie SMS that get sent at 8 am and 10 pm daily'''

import datetime as dt
import pytz
import logging
import settings
from flask import current_app
from sqlalchemy import exists, and_
from app import db
from app.models import AppUser, Notification, Task
from app.queries import notify
from app.routers import get_router, ChooseTask, MorningConfirmation, DidYouDoIt


def main():
    '''get notifications from db and run the appropriate ones'''

    # set up margins to determine which notifs to run based on current time
    margin = dt.timedelta(minutes=10)
    utc_time = dt.datetime.now()
    earliest_time = utc_time - margin
    latest_time = utc_time + margin
    counter = 0
    messages = list()
    
    # query all active choose_tasks if there is no task due today
    # if you have no task in the next 24 hours, you can run choose_task notif
    choose_task_notifs = db.session.query(Notification, AppUser).join(AppUser)\
        .filter(
            Notification.active == True,
            Notification.router.in_([ChooseTask.__name__]),
            ~exists().where(
                and_(
                    AppUser.id == Task.user_id,
                    Task.active == True,
                    Task.due_date >= utc_time, 
                    Task.due_date <= utc_time + dt.timedelta(days=1))) 
        ).all()

    # query all active morning confirmations if there is a task already due today
    morning_confirm_notifs = db.session.query(Notification, AppUser).join(AppUser)\
        .filter(
            Notification.active == True,
            Notification.router.in_([MorningConfirmation.__name__]),
            exists().where(
                and_(
                    AppUser.id == Task.user_id,
                    Task.active == True,
                    Task.due_date >= utc_time,
                    Task.due_date <= utc_time + dt.timedelta(days=1)))
        ).all() 
    
    # query all did_you_do_its if a task is due today
    did_you_do_it_notifs = db.session.query(Notification, AppUser).join(AppUser)\
        .filter(
            Notification.active == True,
            Notification.router.in_([DidYouDoIt.__name__]),
            exists().where(
                and_(
                    AppUser.id == Task.user_id,
                    Task.active == True,
                    Task.due_date >= earliest_time,
                    Task.due_date <= latest_time))
        ).all()

    # combine both lists of notifs
    all_notifs = choose_task_notifs + morning_confirm_notifs + did_you_do_it_notifs

    # run each notif based on user's local time
    for (notif, user) in all_notifs:
        user = user.to_dict()
        notif = notif.to_dict()

        notif_tz = pytz.timezone(user['timezone'])
        local_time = dt.datetime.now(notif_tz)
        # TODO(Nico) assumes that every notif gets sent every day
        reminder_local_time = dt.datetime(
            local_time.year, 
            local_time.month, 
            local_time.day, 
            notif['hour'], # hour and minute are saved in db as local time
            notif['minute'], 
            tzinfo=notif_tz)

        reminder_utc_time = reminder_local_time.astimezone(pytz.utc).replace(tzinfo=None)

        
        if earliest_time <= reminder_utc_time <= latest_time:
            router = get_router(notif['router'])()

            results = router.run_pre_actions(user=user, exchange=None)
            router.outbound = router.outbound.format(**results)
            message = notify(user, router)
            messages.append(message.body)
            counter += 1
    
    status = f"{counter} of {len(all_notifs)} active notifications were sent."
    print(status)

    # TODO is this right?
    return current_app.make_response((str(messages), 201))
