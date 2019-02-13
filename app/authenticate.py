"""source: https://developers.google.com/identity/sign-in/ios/backend-auth """
import os
from flask import request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests


def main():
    """Check if the token passed from client is valid"""
    data = request.get_json()
    if "idToken" in data:
        try:
            token = data["idToken"]
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                os.environ.get("IOS_GOOGLE_CLIENT_ID"))

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            user_id = idinfo['sub']

            print("user_id: ", user_id)

            return jsonify({
                "message": ["You da man", "Seriously though."]
            })

        except ValueError:
            # Invalid token
            return jsonify({"error": "User token was not accepted"})
    
    else:
        return jsonify({"error": "idToken is not present in request"})


