'''These functions check whether certain conditions were met for a router to be selected'''
import datetime as dt
import pytz
from app import db
from app.models import Task, AppUser, Team, TeamMember


def task_chosen(user, tomorrow=False, **kwargs):
    '''check if user has a task due later than now'''
    now = dt.datetime.now()
    
    task_chosen = db.session.query(Task).filter(
        Task.user_id == user['id'], 
        Task.active == True,
        Task.due_date >= now).first()

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


def is_afternoon(user, **kwargs):
    '''Check if the local time is after 3pm'''
    tz = db.session.query(AppUser.timezone).filter(AppUser.id == user['id']).one()[0]
    tz = pytz.timezone(tz)
    now = dt.datetime.now(tz=tz)

    if now.hour >= 15:
        return True
    else:
        return False


def is_member_of_team(user, **kwargs):
    '''Check if the user is part of any team'''
    teams = db.session.query(Team).join(TeamMember).filter(TeamMember.user_id == user['id']).all()

    if teams:
        return True
    else:
        return False