from flask import jsonify, request, make_response
from app import db
from app.models import TeamMember
from app.constants import Statuses
from app.api.invite import decode


def post(user):
    """check if code matches a team. if yes, join the team, and return team"""

    data = request.get_json()

    try:
        team = decode(data["code"])
    except Exception:
        message = f"The code {data['code']} was not accepted. Please try again."
        print(message)
        return make_response(jsonify({"message": message}), 400)

    # ensure user is not already on team
    already_team_member = db.session.query(TeamMember).filter(
        TeamMember.user == user,
        TeamMember.team == team).all()

    if len(already_team_member) > 0:
        message = f"You are already a team member of {team.name}."
        print(message)
        return make_response(jsonify({"message": message}), 400)
    
    # add user to team
    team_member = TeamMember(
        user=user,
        team=team,
        inviter=user, # TODO you can only correct this if you make codes specific
        status=Statuses.ACTIVE)

    db.session.add(team_member)
    db.session.commit()

    # return team
    team_dict = {
        "name": team.name,
        "team_id": team.id,
        "founder_id": team.founder_id
    }
    db.session.close()

    return make_response(jsonify(team_dict), 200)
