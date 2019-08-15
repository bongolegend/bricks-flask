from flask import jsonify, request, make_response
from phonenumbers import parse, is_valid_number_for_region
from phonenumbers.phonenumberutil import NumberParseException
from app.models import Team, Invitation
from app import db
from app.tools import send_message
from sqlalchemy.orm.exc import NoResultFound


def post(user):
    """send invitation to phone number. confirmation code is deterministic based on team info"""

    data = request.get_json()

    for key in ["team_id", "phone_number"]:
        if key not in data:
            return make_response(
                jsonify({"message": f"Missing key from json: {key}"}), 401
            )

    try:
        number = parse(data["phone_number"], "US")
        if not is_valid_number_for_region(number, "US"):
            raise NumberParseException(1, "not valid")
    except NumberParseException:
        return make_response(
            jsonify({"message": "Invalid phone number. Please try again."}), 401
        )

    try:
        team = db.session.query(Team).filter(Team.id == data["team_id"]).one()
    except NoResultFound:
        return make_response(
            jsonify({"message": f"Team with id {data['team_id']} not found."}), 401
        )

    number = f"+{number.country_code}{number.national_number}"
    code = encode(team)
    message = (
        f"{user.username} invited you to join their team {team.name} on the Bricks app."
    )
    recipient = {"phone_number": number}

    send_message(recipient, message)
    send_message(
        recipient,
        "Download the app here: https://itunes.apple.com/us/app/stack-a-brick/id1456194944#?platform=iphone",
    )
    send_message(recipient, "Use this code to join their team:")
    send_message(recipient, code)
    # add invitation to db
    invitation = Invitation(user=user, team=team, invitee_phone=number, code=code)
    db.session.add(invitation)
    db.session.commit()
    db.session.close()

    message = f"Invitation sent to {number}"
    return make_response(jsonify({"message": message}), 200)


def encode(team):
    code = str(team.id)[:3].ljust(3, "q") + str(team.founder_id)[:3].ljust(
        3, team.name[0]
    )
    code = code.lower()
    # reverse
    code = code[::-1]

    return code


def decode(code):
    # reverse
    try:
        code = code[::-1]
        code = code.lower()
        team_code = code[:3].strip("q")
        team_id = int(team_code)
        team = db.session.query(Team).filter(Team.id == team_id).one()
        return team
    except:
        raise InvalidCodeError


class InvalidCodeError(Exception):
    pass
