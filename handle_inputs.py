from flask import request, session
from twilio.twiml.messaging_response import MessagingResponse
from response_db import first_contact_df

def main():
    """Respond to input with appropriate output based on conversation state and response_db.py"""

    # TODO (Nico) create permanent storage
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

# TODO(Nico) implement this
# def update_user_state(...):