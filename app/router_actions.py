import datetime as dt
import pytz
from sqlalchemy import func
from app import db
from app.models import AppUser, Notification, Point, Exchange, Task
from config import Config # TODO(Nico) access the config that has been initialized on the app 
    

def insert_notifications(user, choose_task, morning_confirmation, did_you_do_it, **kwargs):
    '''Create two morning and one evening notif. Add notif to scheduler and to db'''

    # find existing notifications
    existing_choose_tasks = Notification.query.filter_by(
        user_id=user['id'], router=choose_task.name).all()
    existing_morning_confimations = Notification.query.filter_by(
        user_id=user['id'], router=morning_confirmation.name).all()
    existing_evening_checkins = Notification.query.filter_by(
        user_id=user['id'], router=did_you_do_it.name).all()
    
    if not existing_choose_tasks:
        notif = Notification(
            router=choose_task.name,
            body=choose_task.outbound,
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            active=True,
            user_id=user['id'])
        db.session.add(notif)
    
    if not existing_morning_confimations:
        notif = Notification(
            router=morning_confirmation.name,
            body=morning_confirmation.outbound,
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            active=False,
            user_id=user['id'])
        db.session.add(notif)

    if not existing_evening_checkins:
        notif = Notification(
            router=did_you_do_it.name,
            body=did_you_do_it.outbound,
            day_of_week='mon-fri',
            hour=21,
            minute=0,
            active=True,
            user_id=user['id'])
        db.session.add(notif)

    db.session.commit()


def update_timezone(inbound, user, **kwargs):
    tz = Config.US_TIMEZONES.get(inbound, None)
    if tz is not None:        
        user_obj = db.session.query(AppUser).filter_by(id=user['id']).one()
        user_obj.timezone = tz
        user['timezone'] = tz

        # update all notifications for that user in the db
        # TODO(Nico) update notifications in the scheduler
        notifs = db.session.query(Notification).filter_by(user_id=user['id']).all()
        for notif in notifs:
            notif.timezone = tz
            
        db.session.commit()

    else:
        raise ValueError('INVALID TIMEZONE CHOICE')

    return tz


def update_username(inbound, user, **kwargs):
    user_obj = db.session.query(AppUser).filter_by(id=user['id']).one()
    user_obj.username = inbound
    user['username'] = inbound
    db.session.commit()


def insert_points(user, value, **kwargs):
    point = Point(value=value, user_id=user['id'])
    db.session.add(point)
    db.session.commit()


def query_points(user, **kwargs):
    points = db.session.query(func.sum(Point.value).label('points')).filter(Point.user_id == user['id']).one()[0]

    if points is None:
        return 0
    else:
        return points


def change_morning_notification(user, choose_task, morning_confirmation, **kwargs):
    '''
    switch the Active status of the two morning notifications, depending on whether
    someone stated their task the night before.
    '''
    choose_task = db.session.query(Notification).filter(
        Notification.user_id == user['id'],
        Notification.router == choose_task.name).one()

    confirmation = db.session.query(Notification).filter(
        Notification.user_id == user['id'],
        Notification.router == morning_confirmation.name).one()
    
    if choose_task.active == confirmation.active:
        raise ValueError('Both morning notifications are active')
    elif choose_task.active:
        confirmation.active = True
        choose_task.active = False
        print('Switched the active morning notification to CONFIRMATION.')
    elif confirmation.active:
        confirmation.active = False
        choose_task.active = True
        print('Switched the active morning notification to CHOOSE_TASK.')

    db.session.commit()


def query_task(user, choose_task, choose_tomorrow_task, **kwargs):
    '''query the latest task'''
    exchange = db.session.query(Exchange).filter(
        Exchange.user_id == user['id'],
        Exchange.router_id.in_(choose_task.name, choose_tomorrow_task.name)
    ).order_by(Exchange.created.desc()).first()

    return exchange.inbound


def insert_task(user, exchange, inbound, choose_task, choose_tomorrow_task,  **kwargs):
    '''insert task based on input, and set all other tasks with the same due date to inactive'''

    today = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    # determine the due date based on the router id
    if exchange['router'] == choose_task.name:
        due_date = today
    elif exchange['router'] == choose_tomorrow_task.name:
        due_date = datetime.date.today() + datetime.timedelta(days=1)
    else:
        raise NotImplementedError(f"The router {exchange['router']} is not valid for inserting tasks.")

    # create a new task
    new_task = Task(
        description = inbound,
        due_date = due_date,
        active = True,
        exchange_id = exchange['id'],
        user_id = user['id'])
    
    # set any tasks that are already for that day to inactive
    existing_tasks = db.session.query(Task).filter(
        Task.due_date == due_date,
        Task.user_id == user['id'],
    ).all()

    for existing_task in existing_tasks:
        existing_task.active = False
    
    db.session.add(new_task)
    db.session.commit()


def leaderboard(**kwargs):
    '''Make a leaderboard across all users, returning the top 5'''
    users = db.session.query(AppUser.username, func.sum(Point.value))\
        .join(Point)\
        .group_by(AppUser.username)\
        .order_by(func.sum(Point.value).desc())\
        .limit(10)\
        .all()
    
    leaderboard = "{username:_<12}{points}\n".format(username='USERNAME', points='POINTS')
    for user, value in users:
        leaderboard = leaderboard + "{user:_<20}{value}\n".format(user=user[:16], value=value)

    return leaderboard