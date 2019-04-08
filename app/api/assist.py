from flask import jsonify, request, make_response
from app import db
from app.models import Assist


def post(user):
    """api that tracks the assists you lent to your friends"""

    data = request.get_json()

    assist = Assist(
        user = user,
        action = data["action"],
        assistee_member_id = data["assistee_member_id"]
    )

    db.session.add(assist)
    db.session.commit()
    db.session.close()
    message = "Assist posted."

    return make_response(jsonify({"message": message}), 200)
