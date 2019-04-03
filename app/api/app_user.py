""" save the values to app_user. 
device token: this will be used to send push notifications"""


from flask import jsonify, request, make_response
import datetime as dt
from app.models import AppUser, Task
from app import db


def put(user):
    """update user in db"""

    data = request.get_json()
    
    if "device_token" in data:
        user.device_token = data["device_token"]
    if "username" in data:
        user.username = data["username"]
    if "fir_push_notif_token" in data:
        user.fir_push_notif_token = data["fir_push_notif_token"]
    if "fir_auth_id" in data:
        user.fir_auth_id = data["fir_auth_id"]
    if "email" in data:
        user.email = data["email"]

    db.session.commit()
    db.session.close()

    message = "success"
    return make_response(jsonify({"message": message}), 200)
