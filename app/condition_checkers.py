'''These functions check whether certain conditions were met for a router to be selected'''
import datetime as dt
from app import db
from app.models import Exchange, AppUser


def task_chosen(user, **kwargs):
    '''check if a task has been chosen for today'''
    task_chosen_today = db.session.query(Exchange).filter(
        Exchange.user_id==user['id'], 
        Exchange.router_id=='choose_task',
        Exchange.inbound.isnot(None),
        Exchange.created>=dt.date.today()).first()

    if task_chosen_today:
        return True
    return False


def timezone_set(user, **kwargs):
    '''check if timezone has been set for this user'''
    timezone_set = db.session.query(AppUser).filter(
        AppUser.id==user['id'],
        AppUser.timezone.isnot(None)).all()
    if timezone_set:
        return True
    return False


CONDITION_CHECKERS = dict(
    task_chosen = task_chosen,
    timezone_set = timezone_set,
)