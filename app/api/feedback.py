from flask import jsonify, request, make_response
from app import db
from app.models import Feedback
from app.tools import send_message
import os


def post(user):
    """save feedback object to db and send sms to Nico"""

    data = request.get_json()

    for key in ["text"]:
        if key not in data:
            return make_response(
                jsonify({"message": f"Missing key in json: {key}"}), 401
            )

    feedback = Feedback(user=user, text=data["text"])

    db.session.add(feedback)
    db.session.commit()

    message = f"{user.username} suggests: {data['text']}"

    send_message({"phone_number": os.environ.get("NICO_PHONE_NUMBER")}, message)

    message = "Thanks! Feedback received."

    db.session.close()
    return make_response(jsonify({"message": message}), 200)
