from app import db
from app.models import Notification, Task


def insert_notifications(user, choose_task, morning_confirmation, did_you_do_it, **kwargs):
    '''Create two morning and one evening notif. Add notif to db. pass the input classes as instances'''

    # create choose_task notif
    notif = Notification(
        router=choose_task.__name__,
        body=choose_task.outbound,
        day_of_week='mon-fri',
        hour=8,
        minute=0,
        active=True,
        user_id=user['id'])
    db.session.add(notif)
    
    # create morning confirm notif
    notif = Notification(
        router=morning_confirmation.__name__,
        body=morning_confirmation.outbound,
        day_of_week='mon-fri',
        hour=8,
        minute=0,
        active=True,
        user_id=user['id'])
    db.session.add(notif)

    # create did you do it notif
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