"""source: https://developers.google.com/identity/sign-in/ios/backend-auth """
import os
from flask import request, jsonify
from google.oauth2 import id_token
from google.auth.transport import requests
from app import db
from app.models import AppUser

def main():
    """
    Check if the google token passed from client is valid. 
    if yes, find matching user and issue flask token.
    """
    data = request.get_json()
    if "google_token" not in data:
        return jsonify({"error": "google_token is not present in request"})
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
            return jsonify({"error": f"The google token <{google_token}> was not accepted"})

        google_id = google_info['sub']
        print("google_id: ", google_id, type(google_id))
        
        user = query_user(google_id)

        auth_token = user.generate_auth_token()

        return jsonify({'auth_token': auth_token.decode('ascii'), 'duration': 600})
        

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