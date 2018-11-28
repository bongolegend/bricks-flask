import datetime as dt
from app import scheduler, db
from app.models import User, Notification
from app.send_notifications import add_notif_to_scheduler
from config import Config # TODO(Nico) access the config that has been initialized on the app 


def schedule_reminders(last_router_id, user, **kwargs):
    '''Create one morning and one evening reminder. Add reminders to scheduler and to db'''

    # set morning reminder
    if len(Notification.query.filter_by(user=user, tag='morning_ask').all()) == 0:
            
        notif = Notification(tag='morning_ask',
            body="What is your brick for today?",
            trigger_type='cron',
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            jitter=30,
            end_date=dt.datetime(2018,11,30),
            timezone=getattr(user, 'timezone', 'America/Los_Angeles'),
            user=user)
        
        # TODO(Nico) it could be problematic to schedule this before committing to db
        add_notif_to_scheduler(scheduler, notif, user.phone_number, Config)
        db.session.add(notif)

    # set evening reminder
    if len(Notification.query.filter_by(user=user, tag='evening_checkin').all()) == 0:
            
        notif = Notification(tag='evening_checkin',
            body="Did you stack your brick today?",
            trigger_type='cron',
            day_of_week='mon-fri',
            hour=21,
            minute=0,
            jitter=30,
            end_date=dt.datetime(2018,11,30),
            timezone=getattr(user, 'timezone', 'America/Los_Angeles'),
            user=user)
        
        # TODO(Nico) it could be problematic to schedule this before committing to db
        add_notif_to_scheduler(scheduler, notif, user.phone_number, Config)
        db.session.add(notif)

    db.session.commit()


def update_timezone(last_router_id, inbound, user, **kwargs):
    tz = Config.US_TIMEZONES.get(inbound, None)
    if tz is not None:
        user.timezone = tz
        
        # update all notifications for that user in the db
        # TODO(Nico) update notifications in the scheduler
        notifs = db.session.query(Notification).filter_by(user=user).all()
        for notif in notifs:
            notif.timezone = tz
            
        db.session.commit()


    else:
        raise ValueError('INVALID TIMEZONE CHOICE')

    return tz