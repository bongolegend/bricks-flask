'''These functions check whether certain conditions were met for a router to be selected'''
import datetime as dt
from app import db
from app.models import Task, AppUser


def task_chosen(user, tomorrow=False, **kwargs):
    '''check if a task has been chosen for today or tomorrow'''
    due_date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    if tomorrow:
        due_date = due_date + dt.timedelta(days=1)
    
    task_chosen = db.session.query(Task).filter(
        Task.user_id == user['id'], 
        Task.active == True,
        Task.due_date == due_date).first()

    if task_chosen:
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
