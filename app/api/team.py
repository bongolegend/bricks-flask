import traceback
from flask import jsonify, request, make_response
from sqlalchemy import func
import datetime as dt
from app.models import AppUser, Task, Point, Team
from app import db
from app.actions.multiplayer import insert_team_beta
from app import push


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
    pass
        