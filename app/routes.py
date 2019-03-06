'''this blueprint gets added as an extension to the main Flask app in __init__'''
import os
from datetime import timedelta
from flask import Blueprint, current_app, session
from app import chat 
from app import notify
from app.api import (
    auth_token,
    task,
    friend_tasks,
    app_user,
    team
)
from app.security import validate_twilio_request, validate_google_cron_request

main = Blueprint('main', __name__)


@main.route("/api/auth_token", methods=['GET'])
def get_auth_token_wrapper():
    return auth_token.get()

@main.route("/api/task", methods=['PUT'])
@auth_token.verify
def post_task_wrapper(user):
    return task.put(user)

@main.route("/api/friend_tasks", methods=["GET"])
@auth_token.verify
def get_friend_tasks_wrapper(user):
    return friend_tasks.get(user)

@main.route("/api/app_user", methods=["PUT"])
@auth_token.verify
def put_app_user_wrapper(user):
    return app_user.put(user)

@main.route("/api/team", methods=["PUT"])
@auth_token.verify
def put_team_wrapper(user):
    return team.put(user)

@main.route("/")
def landing_page():
    return f"""
<plaintext>

   welcome to Bricks.

         _______
      __/______/|___  
    /___|__ ___|/__/|
    |______|_______|/


Please text {os.environ.get('TWILIO_PHONE_NUMBER')} to get started.
"""


@main.route( "/chat", methods=['GET', 'POST'])
@validate_twilio_request
def conduct_conversations_wrapper():
    return chat.main()


@main.route("/notify", methods=['GET'])
@validate_google_cron_request
def send_notifications_wrapper():
    return notify.main()


# TODO(Nico) is this the right place to put this?
@current_app.before_request
def session_timeout():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(seconds=10)