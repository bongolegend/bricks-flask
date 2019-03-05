import traceback
from flask import jsonify, request, make_response
from sqlalchemy import func
import datetime as dt
from app.models import AppUser, Task, Point
from app import db
from app.actions.multiplayer import get_current_team_members_beta
from app import push


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
            user=user,
            points_total=get_total_points(user))
        
        db.session.add(new_task)


        
        message = "new task successfully created"
        return_task = new_task

        # send push notification to friends
        try:
            friends = get_current_team_members_beta(user, exclude_user=False)
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
        existing_task.points_total = get_total_points(user)

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
        "points_earned": return_task.points_earned,
        "points_total": return_task.points_total
    }

    json = jsonify(task_dict)
    return make_response(json, 200)
    

def add_points(user, grade):
    """Give the user points based on their multiplier"""
    value = grade * 2
    point = Point(user=user, value=value)
    db.session.add(point)
    db.session.commit()

    return value


def get_total_points(user):
    '''Get the total points for this user'''
    value = db.session.query(func.sum(Point.value))\
        .filter(Point.user == user).one()[0]

    if value is None:
        return 0
    else:
        return value

        