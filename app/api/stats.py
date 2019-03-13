"""API that returns the user stats. I expect this to be called frequently as different actions occur."""
from flask import jsonify, request, make_response
from app import db
from app.models import TeamMember
from app.constants import Statuses
from app.api.invite import decode
from app.api.task import get_total_points


def get(user):
    """return user stats"""

    points = get_total_points(user.id)

    stats_dict = {
        "points_total": points,
    }

    return make_response(jsonify(stats_dict), 200)

