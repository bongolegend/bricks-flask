'''
template from twilio's docs
https://www.twilio.com/docs/sms/tutorials/how-to-create-sms-conversations-python

remember that you need to set the ngrok URL every time you restart the ngrok server
https://dashboard.ngrok.com/get-started
'''
import os
import settings
from flask import Flask, request, session # how does Flask just know this stuff?
from twilio.twiml.messaging_response import MessagingResponse
from responses import first_contact_df


SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
app = Flask(__name__) # initialize flask app with this file name so it can be found
app.config.from_object(__name__)


# use a decorator that extends the below func. give it a URL api endpoint with two REST methods
# notice this func is getting tacked on to the Flask app. the app is calling it under the hood
# when the api gets hit
@app.route("/sms", methods=['GET', 'POST']) 
def reply():
    """Respond to input with appropriate output based on conversation flow and responses.py"""

    # get values from session storage
    counter = session.get('counter', 0)
    last_output = session.get('last_output', None)
    last_output_id = session.get('last_output_id', None)

    # process input
    input = request.values.get('Body')
    print('USER INPUT: ', input,' - ', type(input))

    # decide on output
    output, output_id = choose_output(last_output_id, input, first_contact_df)

    resp = MessagingResponse() # initialize twilio's response tool. it works under the hood
    resp.message(output)

    # save new values to session
    counter += 1
    session['counter'] = counter
    session['last_output'] = output
    session['last_output_id'] = output_id

    return str(resp)


def choose_output(last_output_id, input, first_contact_df):
    responses = first_contact_df.copy()
    
    # check last_output_id matches
    if last_output_id is not None:
        filtered = responses[responses.last_output_id == last_output_id]
    else:
        filtered = responses[responses.last_output_id.isnull()]

    # check input matches
    if input in filtered.input.values: # ASSUME that each last_output_id, input pair is unique
        filtered = filtered[filtered.input == input]
    else: # if there is no matching key, use Null as the wildcard
        filtered = filtered[filtered.input.isnull()] # if there are no wildcard options for this key, you get an empty df

    if len(filtered) == 0:
        return "No valid response in our db. Restarting the chat from the beginning.", None

    return filtered.response.iloc[0], int(filtered.index.values[0])
    

if __name__ == "__main__":
    app.run(debug=True)