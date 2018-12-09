import datetime as dt
from sqlalchemy import func
from app import db
from app.models import AppUser, Notification, Point, Exchange
from app.routers import nodes
from config import Config # TODO(Nico) access the config that has been initialized on the app 
    

def schedule_reminders(user, **kwargs):
    '''Create one morning and one evening reminder. Add reminders to scheduler and to db'''

    # set morning choose task
    if len(Notification.query.filter_by(user_id=user['id'], router_id='choose_task').all()) == 0:

        outbound = nodes[nodes.router_id == 'choose_task'].iloc[0]

        notif = Notification(
            router_id=outbound.router_id,
            body=outbound.outbound,
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            active=True,
            user_id=user['id'])
        
        db.session.add(notif)
    
    # set morning confirmation
    if len(Notification.query.filter_by(user_id=user['id'], router_id='morning_confirmation').all()) == 0:

        outbound = nodes[nodes.router_id == 'morning_confirmation'].iloc[0]

        notif = Notification(
            router_id=outbound.router_id,
            body=outbound.outbound,
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            active=False,
            user_id=user['id'])
        
        db.session.add(notif)

    # set evening reminder
    if len(Notification.query.filter_by(user_id=user['id'], router_id='evening_checkin').all()) == 0:

        outbound = nodes[nodes.router_id == 'evening_checkin'].iloc[0]

        notif = Notification(
            router_id=outbound.router_id,
            body=outbound.outbound,
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
        Notification.router_id == 'choose_task').one()

    confirmation = db.session.query(Notification).filter(
        Notification.user_id == user['id'],
        Notification.router_id == 'morning_confirmation').one()
    
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

ROUTER_ACTIONS = dict(
    schedule_reminders = schedule_reminders,
    update_timezone = update_timezone,
    update_username = update_username,
    add_point = add_point,
    query_points = query_points,
    change_morning_notification = change_morning_notification
)