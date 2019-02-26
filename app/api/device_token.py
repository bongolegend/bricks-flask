""" save the ios device token to the user. this will be used to send push notifications"""


from flask import jsonify, request, make_response
import datetime as dt
from app.models import AppUser, Task
from app import db


def put(user):

    data = request.get_json()

    if data["device_token"] is None:
        message = "missing key device_token"
        
        return make_response(jsonify(message), 400)
    
    user.device_token = data["device_token"]

    db.session.commit()

    message = "success"
    return make_response(jsonify(message), 200)
