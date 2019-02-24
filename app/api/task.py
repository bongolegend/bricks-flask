from flask import jsonify, request, make_response
import datetime as dt
from app.models import AppUser, Task
from app import db

def post(user):

    data = request.get_json()
    if "today_task" not in data or "due_date" not in data:
        message = "today_task or due_date not in body"
        print(message)
        json = jsonify({"error_code": "MISSING_KEY", "message": message})
        return make_response(json, 400)

    description = data["today_task"]
    due_date = dt.datetime.strptime(data["due_date"], "%Y-%m-%d")

    # set old task of today to inactive
    old_task = db.session.query(Task).filter(
        Task.user == user,
        Task.due_date == due_date,
        Task.active == True).first()

    if old_task:
        old_task.active = False
        db.session.add(old_task)

    # create new task
    task = Task(
        description=description,
        due_date=due_date,
        active=True,
        user=user)
    
    db.session.add(task)
    db.session.commit()
    
    message = "today_task successfully inserted"
    print(message)
    json = jsonify({"message": message, "task": description})
    return make_response(json, 200)
