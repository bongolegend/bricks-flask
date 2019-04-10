from flask import jsonify, request, make_response
from app.models import AppUser, TeamMember
from app import db
from app.push import notify_user, send_data_notif
from app.constants import Statuses


def post(user):
    """send a push notification to nudge the user"""

    data = request.get_json()

    team_id = data["team_id"]

    # get team members for this team
    team_members = db.session.query(AppUser.fir_push_notif_token).join(
        TeamMember.user
    ).filter(
        TeamMember.team_id == team_id,
        TeamMember.status == Statuses.ACTIVE,
        TeamMember.user_id != user.id
    ).all()

    for member in team_members:
        if member.fir_push_notif_token is not None:
            send_data_notif(member.fir_push_notif_token, 1)

    message = "Data notifications sent to team members"
    return make_response(jsonify({"message": message}), 200)
