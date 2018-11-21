'''this blueprint gets added as an extension to the main Flask app in __init__'''
from flask import Blueprint
import app.conduct_conversations as conduct_conversations


main = Blueprint('main', __name__)

@main.route( "/sms", methods=['GET', 'POST']) 
def conduct_conversations_wrapper():
    return conduct_conversations.main()