'''
template from twilio's docs
https://www.twilio.com/docs/sms/tutorials/how-to-create-sms-conversations-python

remember that you need to set the ngrok URL every time you restart the ngrok server
https://dashboard.ngrok.com/get-started
'''
import logging
from app.base_init import init_db, init_app


# initialize logging so that `flask run` logs the scheduler
logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s - %(message)s')
logger.setLevel(logging.INFO)


db = init_db() # this needs to be instantiated here, else the manage.py and models.py import different `db`
import app.models # relies on importing db, and is necessary for migrations to work, tho circular

def create_app(test=False):
    
    app = init_app(test=test)
    db.init_app(app)
    
    with app.app_context():
        from app.routes import main as main_blueprint
        app.register_blueprint(main_blueprint)

    return app


if __name__ == "__main__":

    app = create_app()
    app.run(debug=True, ssl_context='adhoc')