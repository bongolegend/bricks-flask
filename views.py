from flask import Blueprint
import handle_inputs 

main = Blueprint('main', __name__)

# use a decorator that extends the below func. give it a URL api endpoint with two REST methods
# notice this func is getting tacked on to the Flask app. the app is calling it under the hood
# when the api gets hit
@main.route( "/sms", methods=['GET', 'POST']) 
def handle_inputs_wrapper():
    return handle_inputs.main()