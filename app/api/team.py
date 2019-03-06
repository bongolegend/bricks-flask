import traceback
from flask import jsonify, request, make_response
from app.models import AppUser, Team, TeamMember
from app import db
from app.actions.multiplayer import insert_team_beta
from app.constants import Statuses


def main(user):
    if request.method == "PUT":
        return put(user)
    if request.method == "GET":
        return get(user)
    else:
        raise Exception


def put(user):

    data = request.get_json()

    if data["team_id"] is None:
        team = insert_team_beta(user, data["name"])
    else:
        # update_team(user, data["team_id"], data["name"])
        pass
        
    message = "new team successfully created"

    team_dict = {
        "name": team.name,
        "team_id": team.id,
        "founder": user.username,
        "founder_id": team.founder_id
    }

    json = jsonify(team_dict)
    return make_response(json, 200)


def get(user):
    """return all teams for user"""

    keys = ("team_id", "name", "founder_id", "founder")
    teams = db.session.query(Team.id, Team.name, Team.founder_id, AppUser.username)\
        .join(Team.founder, Team.members)\
        .filter(
            TeamMember.user_id == user.id,
            TeamMember.status == Statuses.ACTIVE).all()

    if len(teams) > 0:
        teams = [dict(zip(keys, team)) for team in teams]

        return make_response(jsonify(teams), 200)
    
    else:
        return make_response(jsonify(list()), 200)

        