from flask import jsonify, request, make_response
from app.models import AppUser


def main():
    if "Authorization" not in request.headers:
        return make_response(jsonify({"error": "provide an auth token as an 'Authorization' header value."}), 409)

    auth_token = request.headers["Authorization"].split(" ")[1]

    user = AppUser.verify_auth_token(auth_token)

    if user is None:
        message = f"auth token <{auth_token}> failed verification"
        print(message)
        return make_response(jsonify({"error": message}), 400)

    # return some BS data
    json = jsonify({
        "friends": [
            "Michael", "Jo", "Sam", "Frodo"
        ]
    })

    return make_response(json, 200)

