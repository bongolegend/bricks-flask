from flask import jsonify, request, make_response
from app.models import AppUser


def main(user):
    print("user received is: ", user)
    # return some BS data
    json = jsonify({
        "friends": [
            "Michael", "Jo", "Sam", "Frodo"
        ]
    })

    return make_response(json, 200)

