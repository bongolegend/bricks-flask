"""API that returns the user stats. I expect this to be called frequently as different actions occur."""
import datetime as dt
import pytz
from flask import jsonify, request, make_response
from app import db
from app.models import TeamMember, Task
from app.constants import Statuses
from app.api.invite import decode
from app.api.task import get_points_total


def get(user):
    """return user stats"""

    now = dt.datetime.now(tz=pytz.timezone(request.headers["TZ"]))
    today = dt.datetime(year=now.year, month=now.month, day=now.day)

    stats_dict = {
        "points_total": get_points_total(user.id),
        "weekly_grades": get_weekly_grades(user, today),
        "streak": get_streak(user, today)
    }

    return make_response(jsonify(stats_dict), 200)


def get_weekly_grades(user, today):
    """return a list of ints, one for each day of the week. Days without a grade get a zero by default"""
    # find the most recent monday
    last_monday = today - dt.timedelta(days=today.weekday())

    # extract the weekday, grade pairings
    tasks_this_week = db.session.query(Task.due_date, Task.grade).filter(
        Task.due_date >= last_monday,
        Task.user == user,
        Task.active == True
    ).all()

    # fill in missing days
    grades = [0] * 7

    for task in tasks_this_week:
        if task.grade is not None:
            as_int = task.due_date.weekday()
            grades[as_int] = task.grade
  

    return grades

def get_streak(user, today):
    """count the number of consecutive days the user has created a task"""

    streak = 0

    # do not include today
    task_dates = db.session.query(Task.due_date).filter(
        Task.due_date < today,
        Task.active == True,
        Task.user == user
    ).order_by(Task.due_date.desc()).all()

    if len(task_dates) > 0:

        task_dates = [x[0] for x in task_dates]
        task_range = range( (task_dates[0] - task_dates[-1]).days )
        all_dates = [task_dates[0] - dt.timedelta(x) for x in task_range]

        missing = sorted(set(all_dates) - set(task_dates), reverse=True)
        
        if len(missing) > 0:
            streak = all_dates.index(missing[0])

    today_task = db.session.query(Task).filter(
        Task.due_date == today,
        Task.active == True,
        Task.user == user
    ).first()

    if today_task is not None:
        return streak + 1
    else:
        return streak
        