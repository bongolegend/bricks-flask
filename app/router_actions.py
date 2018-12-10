import datetime as dt
import pytz
from sqlalchemy import func
from app import db
from app.models import AppUser, Notification, Point, Exchange, Task
from app.routers import ChooseTask, MorningConfirmation, DidYouDoIt
from config import Config # TODO(Nico) access the config that has been initialized on the app 
    

def insert_notifications(user, **kwargs):
    '''Create two morning and one evening notif. Add notif to scheduler and to db'''

    # find existing notifications
    existing_choose_tasks = Notification.query.filter_by(
        user_id=user['id'], router=ChooseTask.name).all()
    existing_morning_confimations = Notification.query.filter_by(
        user_id=user['id'], router=MorningConfirmation.name).all()
    existing_evening_checkins = Notification.query.filter_by(
        user_id=user['id'], router=DidYouDoIt.name).all()
    
    if not existing_choose_tasks:
        notif = Notification(
            router=ChooseTask.name,
            body=ChooseTask.outbound,
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            active=True,
            user_id=user['id'])
        db.session.add(notif)
    
    if not existing_morning_confimations:
        notif = Notification(
            router=MorningConfirmation.name,
            body=MorningConfirmation.outbound,
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            active=False,
            user_id=user['id'])
        db.session.add(notif)

    if not existing_evening_checkins:
        notif = Notification(
            router=DidYouDoIt.name,
            body=DidYouDoIt.outbound,
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


def add_point(user, **kwargs):
    point = Point(value=1, user_id=user['id'])
    db.session.add(point)
    db.session.commit()


def query_points(user, **kwargs):
    points = db.session.query(func.sum(Point.value).label('points')).filter(Point.user_id == user['id']).one()[0]

    if points is None:
        return 0
    else:
        return points


def change_morning_notification(user, **kwargs):
    '''
    switch the Active status of the two morning notifications, depending on whether
    someone stated their task the night before.
    '''
    choose_task = db.session.query(Notification).filter(
        Notification.user_id == user['id'],
        Notification.router == ChooseTask.name).one()

    confirmation = db.session.query(Notification).filter(
        Notification.user_id == user['id'],
        Notification.router == MorningConfirmation.name).one()
    
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


def query_task(user, **kwargs):
    '''query the latest task'''
    exchange = db.session.query(Exchange).filter(
        Exchange.user_id == user['id'],
        Exchange.router_id.in_('choose_task', 'choose_tomorrow_task')
    ).order_by(Exchange.created.desc()).first()

    return exchange.inbound


def insert_task(user, exchange, inbound, **kwargs):
    '''insert task based on input, and set all other tasks with the same due date to inactive'''

    today = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    # determine the due date based on the router id
    if exchange['router'] == 'choose_task':
        due_date = today
    elif exchange['router'] == 'choose_tomorrow_task':
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


ROUTER_ACTIONS = dict(
    insert_notifications = insert_notifications,
    update_timezone = update_timezone,
    update_username = update_username,
    add_point = add_point,
    query_points = query_points,
    change_morning_notification = change_morning_notification,
    insert_task = insert_task
)