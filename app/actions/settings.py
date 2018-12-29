import datetime as dt
import pytz
from app import db
from app.models import AppUser, Task
from app.constants import US_TIMEZONES


def update_timezone(inbound, user, **kwargs):
    '''Update AppUser.timezone for given user. Assumes inbound has been parsed.
        Also update any tasks that have future due dates.
    '''
    old_tz = user['timezone']
    new_tz = US_TIMEZONES[inbound] 

    user_obj = db.session.query(AppUser).filter_by(id=user['id']).one()
    user_obj.timezone = new_tz

    ### update user's upcoming tasks
    # query upcoming tasks
    tasks = db.session.query(Task).filter(
        Task.user_id == user['id'],
        Task.active == True,
        Task.due_date >= dt.datetime.now()).all()
    
    if tasks:
        old_tz = pytz.timezone(old_tz)
        new_tz = pytz.timezone(new_tz)

        old_offset = old_tz.utcoffset(dt.datetime.now()).total_seconds()/3600
        new_offset = new_tz.utcoffset(dt.datetime.now()).total_seconds()/3600
        shift = new_offset - old_offset

        # shift each due date by the change in tz
        for task in tasks:
            task.due_date = task.due_date - dt.timedelta(hours=shift)
    
    db.session.commit()
    return new_tz


def update_username(inbound, user, **kwargs):
    '''Update AppUser.username for given user.'''
    user_obj = db.session.query(AppUser).filter_by(id=user['id']).one()
    user_obj.username = inbound
    user['username'] = inbound
    db.session.commit()
    return inbound
