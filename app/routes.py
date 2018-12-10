'''this blueprint gets added as an extension to the main Flask app in __init__'''
import os
from datetime import timedelta
from flask import Blueprint, current_app, session
import app.conduct_conversations as conduct_conversations
from app.send_notifications import main as send_notifications

main = Blueprint('main', __name__)

# TODO(Nico) protect this endpoint
@main.route( "/sms", methods=['GET', 'POST']) 
def conduct_conversations_wrapper():
    return conduct_conversations.main()

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

@main.route("/notifications", methods=['GET'])
def send_notifications_wrapper():
    return send_notifications()


# TODO(Nico) is this the right place to put this?
@current_app.before_request
def session_timeout():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(seconds=10)