from flask import jsonify, request, make_response
from app import db
from app.models import Feedback
from app.tools import send_message
import os


def post(user):
    """check if code matches a team. if yes, join the team, and return team"""

    data = request.get_json()

    feedback = Feedback(
        user=user,
        text=data["text"])
    
    db.session.add(feedback)
    db.session.commit()

    message = f"{user.username} suggests: {data['text']}"
    
    send_message({"phone_number": os.environ.get("NICO_PHONE_NUMBER")}, message)

    message = "Thanks! Feedback received."
    print(message)
    return make_response(jsonify({"message": message}), 200)

    
