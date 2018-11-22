'''
template from twilio's docs
https://www.twilio.com/docs/sms/tutorials/how-to-create-sms-conversations-python

remember that you need to set the ngrok URL every time you restart the ngrok server
https://dashboard.ngrok.com/get-started
'''
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config


# initialize sqlalchemy and scheduler before app, these are imported into downstream modules
db = SQLAlchemy()
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

def create_app(config=None):
    if config is None:
        config = Config
        
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app) # connects sqlalchemy to flask

    with app.app_context():
        from app.views import main as main_blueprint
        app.register_blueprint(main_blueprint)

        from app.send_notifications import main as send_notifications
        send_notifications(db, scheduler=scheduler)

    return app


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(message)s')
    logger.setLevel(logging.INFO)

    app = create_app(Config)
    app.run(debug=True)