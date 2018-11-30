'''this blueprint gets added as an extension to the main Flask app in __init__'''
import os
from datetime import timedelta
from flask import Blueprint, current_app, session
import app.conduct_conversations as conduct_conversations


main = Blueprint('main', __name__)

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

# TODO(Nico) is this the right place to put this?
@current_app.before_request
def session_timeout():
    session.permanent = True
    current_app.permanent_session_lifetime = timedelta(seconds=10)