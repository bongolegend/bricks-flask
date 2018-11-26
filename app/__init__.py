'''
template from twilio's docs
https://www.twilio.com/docs/sms/tutorials/how-to-create-sms-conversations-python

remember that you need to set the ngrok URL every time you restart the ngrok server
https://dashboard.ngrok.com/get-started
'''
import logging
from app.base_init import init_scheduler, init_db, init_app


# initialize logging so that `flask run` logs the scheduler
logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s - %(message)s')
logger.setLevel(logging.INFO)


scheduler = init_scheduler() # needs to be instantiated here for imports to get the same scheduler instance
db = init_db() # this needs to be instantiated here, else the manage.py and models.py import different `db`

def create_app():
    
    app = init_app()
    db.init_app(app)

    with app.app_context():
        from app.views import main as main_blueprint
        app.register_blueprint(main_blueprint)

        from app.send_notifications import seed_scheduler
        seed_scheduler()

    return app


if __name__ == "__main__":

    app = create_app()
    app.run(debug=True)