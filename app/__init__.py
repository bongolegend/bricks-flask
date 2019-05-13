'''
template from twilio's docs
https://www.twilio.com/docs/sms/tutorials/how-to-create-sms-conversations-python

remember that you need to set the ngrok URL every time you restart the ngrok server
https://dashboard.ngrok.com/get-started
'''
import logging
from app.base_init import init_db, init_app, CustomJSONEncoder
import firebase_admin
from settings import APP_ROOT
import os
import json

# initialize logging so that `flask run` logs the scheduler
logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s - %(message)s')
logger.setLevel(logging.INFO)

# initialize firebase for authentication and push notifications
cred = firebase_admin.credentials.Certificate(os.path.join(APP_ROOT, os.environ.get("FIR_AUTH_KEY")))
# this is a breaking change from using GAE

# json_string = os.environ.get("FIR_AUTH_KEY")
# as_dict = json.loads(json_string)  
# cred = firebase_admin.credentials.Certificate(as_dict)

firebase_admin.initialize_app(cred)

db = init_db() # this needs to be instantiated here, else the manage.py and models.py import different `db`
import app.models # relies on importing db, and is necessary for migrations to work, tho circular

def create_app(test=False):
    
    app = init_app(test=test)
    db.init_app(app)
    app.json_encoder = CustomJSONEncoder

    with app.app_context():
        from app.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)

    return app


if __name__ == "__main__":

    app = create_app()
    app.run(debug=True, ssl_context='adhoc')