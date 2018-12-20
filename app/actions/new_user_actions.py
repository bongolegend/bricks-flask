from app import db
from app.models import Notification, Task


def insert_notifications(user, choose_task, morning_confirmation, did_you_do_it, **kwargs):
    '''Create two morning and one evening notif. Add notif to db. pass the input classes as instances'''

    # find existing notifications
    existing_choose_tasks = Notification.query.filter_by(
        user_id=user['id'], router=choose_task.__name__).all()
    existing_morning_confimations = Notification.query.filter_by(
        user_id=user['id'], router=morning_confirmation.__name__).all()
    existing_evening_checkins = Notification.query.filter_by(
        user_id=user['id'], router=did_you_do_it.__name__).all()
    
    if not existing_choose_tasks:
        notif = Notification(
            router=choose_task.__name__,
            body=choose_task.outbound,
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            active=True,
            user_id=user['id'])
        db.session.add(notif)
    
    if not existing_morning_confimations:
        notif = Notification(
            router=morning_confirmation.__name__,
            body=morning_confirmation.outbound,
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            active=True,
            user_id=user['id'])
        db.session.add(notif)

    if not existing_evening_checkins:
        notif = Notification(
            router=did_you_do_it.__name__,
            body=did_you_do_it.outbound,
            day_of_week='mon-fri',
            hour=21,
            minute=0,
            active=True,
            user_id=user['id'])
        db.session.add(notif)

    db.session.commit()