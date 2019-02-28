from flask import jsonify, request, make_response
import datetime as dt
from app.models import AppUser, Task
from app import db
from app.actions.multiplayer import get_current_team_members_beta
from app import push


def put(user):

    data = request.get_json()
    due_date = dt.datetime.strptime(data["due_date"], "%Y-%m-%d")

    if data["task_id"] is None:
        # create new task
        new_task = Task(
            description=data["description"],
            due_date=due_date,
            active=True,
            user=user)
        
        db.session.add(new_task)

        # set any existing tasks with same due_date to INACTIVE
        old_task = db.session.query(Task).filter(
            Task.user == user,
            Task.due_date == due_date,
            Task.active == True).first()

        if old_task:
            old_task.active = False
        
        message = "new task successfully created"
        return_task = new_task

        # send push notification to friends
        friends = get_current_team_members_beta(user, exclude_user=False)
        push.main(user, friends, data["description"])

    
    else:
        # update values of existing task
        existing_task = db.session.query(Task).filter(
            Task.id == data["task_id"]).one()
        
        existing_task.description = data["description"]
        existing_task.grade = data["grade"]
        existing_task.due_date = due_date

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
        "due_date": return_task.due_date
    }

    json = jsonify(task_dict)
    return make_response(json, 200)
    

    

        