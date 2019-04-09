"""API that returns the user stats. I expect this to be called frequently as different actions occur."""
import datetime as dt
from dateutil.relativedelta import relativedelta
import pytz
import traceback
import pandas as pd
from flask import jsonify, request, make_response
from sqlalchemy import func
from app import db
from app.models import TeamMember, Task, Point, AppUser, Assist
from app.constants import Statuses
from app.api.invite import decode


def get(user):
    """return user stats"""

    now = dt.datetime.now(tz=pytz.timezone(request.headers["TZ"]))
    today = dt.datetime(year=now.year, month=now.month, day=now.day)

    rank, total_users = get_rank(user, today)
    consistency, count_graded_tasks = get_consistency(user.id)
    assistance, today_assist = get_assistance(user.id, today)
    stats_dict = {
        "points_total": get_points_total(user.id),
        "weekly_grades": get_weekly_grades(user, today),
        "streak": get_streak(user, today),
        "rank": rank,
        "total_users": total_users,
        "consistency": consistency,
        "count_graded_tasks": count_graded_tasks,
        "assistance": assistance,
        "today_assist": today_assist,
        "monthly_graded_tasks": get_tasks_this_month(user.id, today)
    }
    db.session.close()


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
    """count the number of consecutive days the user has graded a task"""

    streak = 0
    yesterday = today - dt.timedelta(1)

    # do not include today
    task_dates = db.session.query(Task.due_date).filter(
        Task.due_date < today,
        Task.active == True,
        Task.grade != None,
        Task.user == user
    ).order_by(Task.due_date.desc()).all()

    if len(task_dates) > 0:

        task_dates = [x[0] for x in task_dates]
        # number of days since your first task
        task_range = range( (yesterday - task_dates[-1]).days )
        # all dates since your first task
        all_dates = [yesterday - dt.timedelta(x) for x in task_range]

        missing = sorted(set(all_dates) - set(task_dates), reverse=True)
        
        if len(missing) > 0:
            streak = all_dates.index(missing[0])

    today_task = db.session.query(Task).filter(
        Task.due_date == today,
        Task.active == True,
        Task.grade != None,
        Task.user == user
    ).first()

    # count today as part of the streak
    if today_task is not None:
        return streak + 1
    else:
        return streak

def get_rank(user, today):
    """get the overall rank for the user"""

    # totals = db.session.query(Point.user_id, func.sum(Point.value).label("total"))\
    #     .group_by(Point.user_id).subquery()

    totals = db.session.query(Task.user_id, func.count(Task.id).label("total"))\
        .filter(
            Task.active == True,
            Task.grade != None
        ).group_by(Task.user_id).subquery()
    
    data = db.session.query(
        AppUser.id, 
        (today - AppUser.created).label("time"),
        totals.c.total
    ).join(
        totals,
        totals.c.user_id == AppUser.id
    ).all()



    data = pd.DataFrame(data, columns=["user_id", "time","total"])

    data["consistency"] = data.total / data.time.apply(lambda x: x.days + 1)

    data = data.sort_values("consistency", ascending=False)

    data = data.reset_index(drop=True)

    rank_list = data.index[
        data.user_id == user.id
    ].tolist()

    if len(rank_list) > 0:
        rank = rank_list[0] + 1
    else:
        rank = len(data.index)

    return rank, len(data.index)

def get_consistency(user_id):
    """calculate consistency score as tasks graded / days on platform"""

    now = dt.datetime.now(tz=pytz.timezone(request.headers["TZ"]))
    today = dt.datetime(year=now.year, month=now.month, day=now.day)

    tasks = db.session.query(func.count(Task.id))\
        .filter(
            Task.active == True,
            Task.user_id == user_id,
            Task.grade != None
        ).one()
    
    days = db.session.query(
        (today - AppUser.created).label("time")
    ).filter(
        AppUser.id == user_id
    ).one()

    consistency = tasks[0] / (days[0].days + 1 ) * 100

    if consistency is None:
        return 0, 0
    else:
        return round(consistency), tasks[0]


def get_assistance(user_id, today):
    """percent of days user assisted a team mate"""

    today_assist = False

    # get assist dates
    distinct_days_with_assists = db.session.query(func.date(Assist.created)).distinct(
        func.date(Assist.created)
    ).filter(
        Assist.user_id == user_id
    ).all()

    # did you assist someone today?
    distinct_days_with_assists = [x[0] for x in distinct_days_with_assists]

    if dt.datetime.now().date() in distinct_days_with_assists:
        today_assist = True


    # get total days on platform
    days_query = db.session.query(
        (today - AppUser.created)
    ).filter(
        AppUser.id == user_id
    ).one()

    count_distinct_assist_days = len(distinct_days_with_assists)
    days = days_query[0].days

    if days <= 1:
        return count_distinct_assist_days, today_assist
    else:
        return round(count_distinct_assist_days / days * 100), today_assist

def get_tasks_this_month(user_id, today):
    """get number of tasks this month"""

    start_of_month = today.replace(day=1)
    next_month = start_of_month + relativedelta(months=1)

    graded_tasks = db.session.query(Task.id).filter(
        Task.user_id == user_id,
        Task.active == True,
        Task.grade != None,
        Task.due_date >= start_of_month,
        Task.due_date < next_month
    ).count()

    return graded_tasks