from flask import jsonify, request, make_response
from app.models import AppUser


def main(user):
    print("user received is: ", user)

    data = request.get_json()

    if "today_task" not in data:
        message = "today_task not in body"
        print(message)
        json = jsonify({"error_code": "MISSING_KEY", "message": message})
        return make_response(json, 400)

    task = data["today_task"]
    print("TASK POSTED is: ", task)

    # make sure the fields make sense

    # insert task into db

    # return success
    message = "today_task successfully inserted"
    print(message)
    json = jsonify({"message": message, "task": task})
    return make_response(json, 200)
