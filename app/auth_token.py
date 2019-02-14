"""source: https://developers.google.com/identity/sign-in/ios/backend-auth """
import os
import functools
from flask import request, jsonify, make_response, current_app
from google.oauth2 import id_token
from google.auth.transport import requests
from passlib.hash import pbkdf2_sha256
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from app import db
from app.models import AppUser


def get():
    """
    api endpoint
    Check if the google token passed from client is valid. 
    if yes, find matching user and issue flask token.
    """
    data = request.get_json()
    if "google_token" not in data:
        json = jsonify({"error": "google_token is not present in request"})
        return make_response(json, 400)
    else:
        try: # verify google token on google
            google_token = data['google_token']
            google_info = id_token.verify_oauth2_token(
                google_token, 
                requests.Request(), 
                os.environ.get("IOS_GOOGLE_CLIENT_ID"))

            if google_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer for google token.')
        except ValueError: # notify client of invalid token
            json = jsonify({"error": f"The google token <{google_token}> was not accepted"})
            return make_response(json, 400)


        google_id = google_info['sub']
        print("google_id: ", google_id, type(google_id))
        
        user = query_user(google_id)

        auth_token, duration = generate(user)

        json = jsonify({'auth_token': auth_token.decode('ascii'), 'duration': duration})
        return make_response(json, 202)
        

def query_user(google_id):
    """find the user that matches google_id, else generate new user"""

    user = db.session.query(AppUser).filter(google_id == google_id).first()

    if user:
        return user
    else:
        new_user = AppUser(google_id=google_id)
        db.session.add(new_user)
        db.session.commit()

        return new_user


# source: https://blog.miguelgrinberg.com/post/restful-authentication-with-flask/page/3
def generate(user, duration=5):
    """generate a new token for the given user"""
    s = Serializer(current_app.config['SECRET_KEY'], expires_in = duration)
    return s.dumps({ 'id': user.id }), duration


def verify(func):
    '''
    wrapper that verifies the token is correct. 
    if yes, passes request to target api endpoint.
    if no, prompts client to re-authenticate.
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "Authorization" not in request.headers:
            return make_response(jsonify({"error": "provide an auth token as an 'Authorization' header value."}), 409)

        auth_token = request.headers["Authorization"].split(" ")[1]

        user = validate(auth_token)

        if user in ["EXPIRED", "BAD_SIGNATURE"]:
            message = f"auth token failed verification because it is {user}"
            print(message)
            return make_response(jsonify({"error_code": user, "message": message, "auth_token": auth_token}), 400)
        
        return func(user, *args, **kwargs)
    return wrapper


def validate(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except SignatureExpired:
        return "EXPIRED"
    except BadSignature:
        return "BAD_SIGNATURE"
    user = AppUser.query.get(data['id'])
    return user