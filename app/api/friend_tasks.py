from flask import jsonify, request, make_response
import dateutil.parser
import datetime as dt
import pytz
from app.models import AppUser, Task, Team, TeamMember
from app.actions.multiplayer import get_current_team_members_beta
from app import db

def get(user):
    """
    get today tasks for your friends and yourself. return data format:
    [
        {
            "username": "jo",
            "task": "pay taxes",
            "grade": 5,
            "user_id": 12,
            "due_date": "2019-02-25"
        }, {
            "name": "mark",
            "task": null, <-- indicate that team member has not submitted a task yet TODO
            "grade": null,
            "user_id": 14
        }
    ]
    """

    if "TZ" not in request.headers:
        message = "Provide TZ in headers"
        return make_response(jsonify({"message": message}), 400)
    
    # get today in user's tz
    now = dt.datetime.now(tz=pytz.timezone(request.headers["TZ"]))
    today = dt.datetime(year=now.year, month=now.month, day=now.day)

    # find friends on team
    team_members = get_current_team_members_beta(user, exclude_user=False)
    member_ids = [member.id for member in team_members]
    
    # filter on due date corresponding to today, irrespective of time zone
    tasks = db.session.query(AppUser.username, AppUser.id, Task.description, Task.grade, Task.due_date).join(Task.user)\
        .filter(
        Task.due_date == today,
        Task.user_id.in_(member_ids),
        Task.active == True).all()
        
    keys = ("username", "user_id", "description", "grade", "due_date")
    tasks = [dict(zip(keys, task)) for task in tasks]

    return make_response(jsonify(tasks), 200)