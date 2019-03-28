"""API that returns the user stats. I expect this to be called frequently as different actions occur."""
import datetime as dt
import pytz
import traceback
import pandas as pd
from flask import jsonify, request, make_response
from sqlalchemy import func
from app import db
from app.models import TeamMember, Task, Point, AppUser
from app.constants import Statuses
from app.api.invite import decode

def get(user):
    """return user stats"""

    now = dt.datetime.now(tz=pytz.timezone(request.headers["TZ"]))
    today = dt.datetime(year=now.year, month=now.month, day=now.day)

    rank, total_users = get_rank(user, today)
    stats_dict = {
        "points_total": get_points_total(user.id),
        "weekly_grades": get_weekly_grades(user, today),
        "streak": get_streak(user, today),
        "rank": rank,
        "total_users": total_users
    }


    return make_response(jsonify(stats_dict), 200)

def get_points_total(user_id):
    '''Get the total points for this user'''
    value = db.session.query(func.sum(Point.value))\
        .filter(Point.user_id == user_id).one()[0]

    if isinstance(value, int):
        return value
    else:
        return 0

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

def get_rank(user, today):
    """get the overall rank for the user"""

    totals = db.session.query(Point.user_id, func.sum(Point.value).label("total"))\
        .group_by(Point.user_id).subquery()
    
    data = db.session.query(
        AppUser.id, 
        (today - AppUser.created).label("time"),
        totals.c.total
    ).join(
        totals,
        totals.c.user_id == AppUser.id
    ).all()

    data = pd.DataFrame(data, columns=["user_id", "time","total"])

    data["score"] = data.total / data.time.apply(lambda x: x.days + 1)

    data = data.sort_values("score", ascending=False)

    data = data.reset_index(drop=True)

    rank = data.index[
        data.user_id == user.id
    ].tolist()[0] + 1

    return rank, len(data.index)
