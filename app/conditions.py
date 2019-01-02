'''These functions check whether certain conditions were met for a router to be selected'''
import datetime as dt
import pytz
from app import db
from app.models import Task, AppUser, Team, TeamMember
from app.constants import Reserved

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


def is_new_user(user, **kwargs):
    '''Check if the user has accepted their invitation yet, by having set a new username'''
    if user['username'] == Reserved.NEW_USER:
        return True
    else:
        return False


def should_give_feedback(user, **kwargs):
    '''Check how many tasks the user has created. At specific counts of tasks
    they should be solicited for feedback'''

    time_to_give_feedback = (3,10,30)

    tasks = db.session.query(Task.id).filter(
        Task.user_id == user['id'],
        Task.active == True).all()
    
    if len(tasks) in time_to_give_feedback:
        return True
    else:
        return False