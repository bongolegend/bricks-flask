import traceback
import pytz
from flask import jsonify, request, make_response
from sqlalchemy import func
import datetime as dt
from app.models import AppUser, Task, Point
from app import db
from app.actions.multiplayer import get_current_team_members_beta
from app import push
import os

def main(user):
    if request.method == "PUT":
        return put(user)
    if request.method == "GET":
        return get(user)
    else:
        raise Exception


def put(user):

    data = request.get_json()
    due_date = dt.datetime.strptime(data["due_date"], "%Y-%m-%d")

    if data["task_id"] is None:
        # set any existing tasks with same due_date to INACTIVE
        old_task = db.session.query(Task).filter(
            Task.user == user,
            Task.due_date == due_date,
            Task.active == True).first()

        if old_task:
            old_task.active = False
            
        # create new task
        new_task = Task(
            description=data["description"],
            due_date=due_date,
            active=True,
            user=user)
        
        db.session.add(new_task)


        
        message = "new task successfully created"
        return_task = new_task


        try:
            if user.id == os.environ.get("NICO_USER_ID"):
                # send push notification to everyone
                all_users = db.session.query(AppUser).filter(
                    AppUser.firebase_token != None,
                    AppUser.id != user.id
                ).all()
                push.task_created(user, all_users, data["description"])
            else:
                # send push notification to friends
                friends = get_current_team_members_beta(user, exclude_user=True)
                push.task_created(user, friends, data["description"])
        
        except Exception as e:
            print("ERROR: PUSH NOTIFICATION FAILED")
            traceback.print_exc()

    
    else:
        # update values of existing task
        existing_task = db.session.query(Task).filter(
            Task.id == data["task_id"]).one()
        existing_task.grade = data["grade"]
        existing_task.points_earned = add_points(user, data["grade"])

        message = "updated existing task"
        return_task = existing_task

    # for all
    db.session.commit()
    print(message)

    task_dict = {
        "username": user.username,
        "user_id": user.id,
        "task_id": return_task.id,
        "description": return_task.description,
        "grade": return_task.grade,
        "due_date": return_task.due_date,
        "points_earned": return_task.points_earned
    }

    json = jsonify(task_dict)
    return make_response(json, 200)
    

def get(user):
    """get the last week's worth of tasks from user"""

    if "TZ" not in request.headers:
        message = "Provide TZ in headers"
        return make_response(jsonify({"message": message}), 400)
    
    # get today in user's tz
    now = dt.datetime.now(tz=pytz.timezone(request.headers["TZ"]))
    today = dt.datetime(year=now.year, month=now.month, day=now.day)
    week_ago = today - dt.timedelta(days=7)

    tasks = db.session.query(Task).filter(
        Task.user == user,
        Task.active == True,
        Task.due_date >= week_ago,
    ).order_by(
        Task.due_date.desc()
    ).all()

    tasks_list = list()
    if len(tasks) > 0:
        for task in tasks:
            tasks_list.append(task.to_dict())

    return make_response(jsonify(tasks_list), 200)


def add_points(user, grade):
    """Give the user points based on their multiplier"""
    value = grade * 2
    point = Point(user=user, value=value)
    db.session.add(point)
    db.session.commit()

    return value



       