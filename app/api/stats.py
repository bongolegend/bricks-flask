"""API that returns the user stats. I expect this to be called frequently as different actions occur."""
import datetime
from flask import jsonify, request, make_response
from app import db
from app.models import TeamMember, Task
from app.constants import Statuses
from app.api.invite import decode
from app.api.task import get_points_total


def get(user):
    """return user stats"""

    points = get_points_total(user.id)
    weekly_grades = get_weekly_grades(user)
    stats_dict = {
        "points_total": points,
        "weekly_grades": weekly_grades
    }

    return make_response(jsonify(stats_dict), 200)


def get_weekly_grades(user):
    """return a list of ints, one for each day of the week. Days without a grade get a zero by default"""
    # find the most recent monday
    today = datetime.date.today()
    last_monday = today - datetime.timedelta(days=today.weekday())

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