"""module for creating push notifications"""
from hyper import HTTPConnection
import os
import calendar
import time
import jwt
import json
from app.constants.Push import ALGORITHM

def main(friends, message):

    # TODO: Apple doesnt want you recreating new tokens all the time, so you may need to implement this section
    # last_token = get_last_token()

    # if last_token.time + 1200 > calendar.timegm(time.gmtime()):
    #     jwt_token = create_jwt()
    # else:
    #     jwt_token = last_token

    jwt_token = create_jwt()

    message = f"{user.username} is gonna do this: {message}."

    for user in friends:
        if user.device_token is not None:
            post_notification(user, jwt_token, message)

def post_notification(user, jwt_token, message):
    """make a POST request to APNs to generate a push notification for user"""

    url_path = f"/3/device/{user.device_token}"

    request_headers = {
        "authorization": jwt_token,
        "method": "POST",
        "path": url_path,
        "apns-topic": "com.ncernek.bricks"
        # "apns-id"  # unique id for this notif
    }

    request_body = {
        "aps": {
            "alert": message
        }
    }

    body_bytes = json.dumps(request_body).encode('utf-8')

    # you may need to compress headers with https://python-hyper.org/hpack/en/latest/

    conn = HTTPConnection(os.environ.get("APNS_DEV_SERVER"))
    # you could use jsonify, but not outside app context
    conn.request('POST', url_path, headers=request_headers, body=body_bytes)
    response = conn.get_response()

    print(response.headers)
    print(response.status)
    print(response.read())


def create_jwt():
    """generate jwt per Apple specs. Refresh your token no more than once every 20 minutes and no less than once every 60 minutes.
    https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server/establishing_a_token-based_connection_to_apns
    """

    jwt_headers = {
    "alg" : ALGORITHM,
    "kid" : os.environ.get("APNS_KEY_ID")
    }

    jwt_payload = {
    "iss": os.environ.get("APPLE_DEVELOPER_TEAM_ID"),
    "iat": calendar.timegm(time.gmtime())
    }

    private_key = open(os.environ.get("AUTH_KEY_PATH"), "r").read()

    encoded_jwt = jwt.encode(
        jwt_payload, 
        private_key, 
        algorithm=ALGORITHM, 
        headers=jwt_headers)

    apple_formatted_jwt = f"bearer {encoded_jwt.decode('ascii')}"

    return apple_formatted_jwt