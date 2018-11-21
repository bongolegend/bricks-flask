'''
template from twilio's docs
https://www.twilio.com/docs/sms/tutorials/how-to-create-sms-conversations-python

remember that you need to set the ngrok URL every time you restart the ngrok server
https://dashboard.ngrok.com/get-started
'''
import os
import logging
import settings
from flask import Flask
import send_notifications
import handle_inputs 


SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
app = Flask(__name__)
app.config.from_object(__name__)

# run the scheduler to send notifications on a schedule
send_notifications.main()

# use a decorator that extends the below func. give it a URL api endpoint with two REST methods
# notice this func is getting tacked on to the Flask app. the app is calling it under the hood
# when the api gets hit
@app.route( "/sms", methods=['GET', 'POST']) 
def handle_inputs_wrapper():
    return handle_inputs.main()


if __name__ == "__main__":
    logger = logging.getLogger()
    logging.basicConfig(format='%(asctime)s - %(message)s')
    logger.setLevel(logging.INFO)

    app.run(debug=True)