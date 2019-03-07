from flask import jsonify, request, make_response
from phonenumbers import parse
from phonenumbers.phonenumberutil import NumberParseException
from app.models import Team
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
    message = f"""
Your friend {user.username} just invited you to join their team {team.name} on Bricks. 
Download the app and use this code after you log in: {code}"""

    # send message to number with Twilio
    send_message({"phone_number": number}, message)

    message = "Invitation sent"
    return make_response(jsonify({"message": message}), 200)


def encode(team):
    code = str(team.id)[:3].ljust(3, "Q") + str(team.founder_id)[:3].ljust(3, team.name[0])
    # reverse
    code = code[::-1]

    return code


def decode(code):
    # reverse
    code = code[::-1]

    team_code = code[:3].strip("Q")
    team_id = int(team_code)

    team = db.session.query(Team).filter(Team.id == team_id).one()

    return team