from flask import jsonify, request, make_response
from phonenumbers import parse
from phonenumbers.phonenumberutil import NumberParseException
from app.models import Team, Invitation
from app import db
from app.tools import send_message
 

def post(user):
    """send invitation to phone number. confirmation code is deterministic based on team info"""

    data = request.get_json()

    try:
        number = parse(data["phone_number"], "US")
    except NumberParseException:
        message = "The number supplied does not seem to be valid. Please try again."
        print(message)
        return make_response(jsonify({"message": message}), 400)


    number = f"+{number.country_code}{number.national_number}"

    # generate a confirmation code
    team = db.session.query(Team).filter(Team.id == data["team_id"]).one()

    code = encode(team)

    # format message
    message = f"{user.username} invited you to join their team {team.name} on the Bricks app. Use this code to join their team:"

    # send message to number with Twilio
    recipient = {"phone_number": number}

    send_message(recipient, message)
    send_message(recipient, code)
    send_message(recipient, "Download the app here: https://testflight.apple.com/join/k4evaAed")

    # add invitation to db
    invitation = Invitation(
        user = user,
        team = team,
        invitee_phone = number,
        code = code
    )
    db.session.add(invitation)
    db.session.commit()
    db.session.close()

    message = f"Invitation sent to {number}"
    return make_response(jsonify({"message": message}), 200)


def encode(team):
    code = str(team.id)[:3].ljust(3, "q") + str(team.founder_id)[:3].ljust(3, team.name[0])
    code = code.lower()
    # reverse
    code = code[::-1]

    return code


def decode(code):
    # reverse
    code = code[::-1]
    code = code.lower()

    team_code = code[:3].strip("q")
    team_id = int(team_code)

    team = db.session.query(Team).filter(Team.id == team_id).one()

    return team