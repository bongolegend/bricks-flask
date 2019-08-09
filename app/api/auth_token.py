"""source: https://firebase.google.com/docs/auth/admin/verify-id-tokens """
import os
import functools
import traceback
from flask import request, jsonify, make_response, current_app
from firebase_admin import auth
from passlib.hash import pbkdf2_sha256
from itsdangerous import (
    TimedJSONWebSignatureSerializer as Serializer,
    BadSignature,
    SignatureExpired,
)
from app import db
from app.models import AppUser
from tests.api.auth_token_test import MOCK_TOKEN, FIR_AUTH_ID


def get():
    """
    api endpoint
    Check if the fir token passed from client is valid. 
    if yes, find matching user and issue flask token.
    """

    if "Authorization" not in request.headers:
        message = "Authorization with fir token is not present in request header"
        return make_response(jsonify({"message": message}), 401)
    else:
        try:
            fir_token = request.headers["Authorization"]
            fir_auth_id = verify_token(fir_token)
        except ValueError:
            message = "The fir token was not accepted"
            print(message)
            return make_response(jsonify({"message": message}), 401)

        user = query_user(fir_auth_id)

        auth_token, duration = generate(user)

        db.session.expunge(user)
        db.session.close()
        json = jsonify(
            {
                "auth_token": auth_token.decode("ascii"),
                "user_id": user.id,
                "duration": duration,
            }
        )
        return make_response(json, 202)


def query_user(fir_auth_id):
    """find the user that matches fir_auth_id, else generate new user"""

    try:
        user = (
            db.session.query(AppUser).filter(AppUser.fir_auth_id == fir_auth_id).one()
        )
        return user
    except:
        new_user = AppUser(fir_auth_id=fir_auth_id)
        db.session.add(new_user)
        db.session.commit()

        return new_user


# source: https://blog.miguelgrinberg.com/post/restful-authentication-with-flask/page/3
def generate(user, duration=86400):
    """generate a new token for the given user"""
    s = Serializer(current_app.config["SECRET_KEY"], expires_in=duration)
    return s.dumps({"id": user.id}), duration


def verify(func):
    """
    wrapper that verifies the token is correct. 
    if yes, passes request to target api endpoint.
    if no, prompts client to re-authenticate.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "Authorization" not in request.headers:
            return make_response(
                jsonify(
                    {
                        "error": "provide an auth token as an 'Authorization' header value."
                    }
                ),
                401,
            )

        auth_token = request.headers["Authorization"].split(" ")[1]

        error, data = validate(auth_token)

        if error:
            message = f"auth token failed verification: {error}"
            print(message)
            return make_response(jsonify({"message": message}), 401)
        elif data:
            user = db.session.query(AppUser).filter(AppUser.id == data["id"]).one()
        else:
            raise Exception

        return func(user, *args, **kwargs)

    return wrapper


def validate(token):
    """read the auth token and return """
    s = Serializer(current_app.config["SECRET_KEY"])
    try:
        data = s.loads(token)
        return None, data
    except SignatureExpired:
        return "EXPIRED", None
    except BadSignature:
        return "BAD_SIGNATURE", None


def verify_token(fir_token):
    """toggle between a mock verifier and the real fir verifier"""
    if current_app.config["TESTING"] == True:
        if fir_token == MOCK_TOKEN:
            return FIR_AUTH_ID
        else:
            raise ValueError
    else:
        decoded_token = auth.verify_id_token(fir_token)
        return decoded_token["uid"]
