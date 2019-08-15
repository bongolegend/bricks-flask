from flask import jsonify, request, make_response
from app import db
from app.models import TeamMember
from app.constants import Statuses
from app.api.invite import decode, InvalidCodeError


def post(user):
    """check if code matches a team. if yes, join the team, and return team"""

    data = request.get_json()

    for key in ["code"]:
        if key not in data:
            return make_response(
                jsonify({"message": f"Missing key in json: {key}"}), 401
            )

    try:
        team = decode(data["code"])
    except InvalidCodeError:
        return make_response(jsonify({"message": f"Invalid code: {data['code']}"}), 401)

    # ensure user is not already on team
    is_already_member = (
        db.session.query(TeamMember)
        .filter(TeamMember.user == user, TeamMember.team == team)
        .one_or_none()
    )

    if is_already_member:
        return make_response(
            jsonify({"message": f"You are already a team member of {team.name}."}), 401
        )

    # add user to team
    team_member = TeamMember(
        user=user,
        team=team,
        inviter=user,  # TODO you can only correct this if you make codes specific
        status=Statuses.ACTIVE,
    )

    db.session.add(team_member)

    response = make_response(jsonify(team.to_dict()), 200)
    db.session.commit()
    db.session.close()
    return response
