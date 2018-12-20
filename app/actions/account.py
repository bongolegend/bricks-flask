from app import db
from app.models import AppUser
from app.constants import US_TIMEZONES


def update_timezone(inbound, user, **kwargs):
    '''Update AppUser.timezone for given user. Assumes inbound has been parsed.'''
    tz = US_TIMEZONES[inbound] 
    user_obj = db.session.query(AppUser).filter_by(id=user['id']).one()
    user_obj.timezone = tz
    user['timezone'] = tz
    db.session.commit()
    return tz


def update_username(inbound, user, **kwargs):
    '''Update AppUser.username for given user.'''
    user_obj = db.session.query(AppUser).filter_by(id=user['id']).one()
    user_obj.username = inbound
    user['username'] = inbound
    db.session.commit()
    return inbound
