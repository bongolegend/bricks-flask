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


db = SQLAlchemy()
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    import send_notifications
    send_notifications.main(scheduler=scheduler)

    return app



if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(message)s')
    logger.setLevel(logging.INFO)

    app = create_app()
    app.run(debug=True)