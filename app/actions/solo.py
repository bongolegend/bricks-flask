import datetime as dt
import pytz
from sqlalchemy import func
from app import db
from app.models import AppUser, Notification, Point, Task
from app.tools import send_message
from app.constants import RouterNames


def insert_points(user, inbound, **kwargs):
    '''insert arbitrary number of points for user. assume that inbound is an integer'''
    point = Point(value=inbound, user_id=user['id'])
    db.session.add(point)
    db.session.commit()


def get_total_points(user, **kwargs):
    '''Get the total points for this user'''
    points = db.session.query(func.sum(Point.value)).filter(Point.user_id == user['id']).one()[0]

    if points is None:
        return 0
    else:
        return points


def get_latest_task(user, **kwargs):
    '''query the latest task'''
    task = db.session.query(Task).filter(
        Task.user_id == user['id'],
        Task.active == True
        ).order_by(Task.due_date.desc()).first()

    return task.description


def insert_task(user, exchange, inbound, **kwargs):
    '''
    insert task based on input, and set all other tasks with the same due date to inactive.
    If the user has team mates, send them a notification of this task.
    '''

    # what day is it for user?
    today_local = dt.datetime.now(tz=pytz.timezone(user['timezone']))

    # what time today are your tasks due? look at the Notif DidYouDoIt
    hour, minute = db.session.query(Notification.hour, Notification.minute).filter(
        Notification.user_id == user['id'],
        Notification.router == RouterNames.DID_YOU_DO_IT,
        Notification.active == True).one()

    # local time that task is due
    due_today_local = today_local.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # convert due_today to utc, then make timezone naive
    due_today = due_today_local.astimezone(pytz.utc).replace(tzinfo=None)

    # determine the due date based on the router id
    if exchange['router'] == RouterNames.CHOOSE_TASK:
        due_date = due_today
    elif exchange['router'] == RouterNames.CHOOSE_TOMORROW_TASK:
        due_date = due_today + dt.timedelta(days=1)
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


def get_username(user, **kwargs):
    '''Get the username for this user'''
    return user['username']


def get_past_tasks(user, **kwargs):
    '''Get the tasks submitted this past week'''

    tasks = db.session.query(Task.description).filter(
        Task.user_id == user['id'],
        Task.active == True,
        Task.due_date > dt.datetime.now() - dt.timedelta(days=7)
    ).all()
    return tasks


def str_past_tasks(user, **kwargs):
    '''get tasks submitted this past week as str'''
    tasks = get_past_tasks(user)

    if not tasks:
        return "You didn't create any tasks this past week."
    
    str_tasks = str()
    for task in tasks:
        str_tasks += '\n- ' + task.description

    return str_tasks 
