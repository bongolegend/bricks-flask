from flask import jsonify, request, make_response
from app.models import AppUser, TeamMember, Team
from app import db
from app.push import notify_user, send_message_notif
from app.constants import Statuses
from sqlalchemy.orm.exc import NoResultFound


def post(user):
    """send a push notification containing a new message to team members of a specific team"""

    data = request.get_json()

    for key in ["team_id", "content"]:
        if key not in data:
            return make_response(
                jsonify({"message": f"Missing key from json: {key}"}), 401
            )

    try:
        db.session.query(Team).filter_by(id=data["team_id"]).one()
    except NoResultFound:
        return make_response(
            jsonify({"message": f"Team with id {data['team_id']} does not exist"}), 401
        )

    team_members = get_team_members(data["team_id"], user.id)

    for member in team_members:
        if member.chat_notifs:
            send_message_notif(
                member.fir_push_notif_token,
                1,
                title=user.username,
                body=data["content"],
            )
        else:
            send_message_notif(member.fir_push_notif_token, 1)

    message = "Data notifications sent to team members"
    return make_response(jsonify({"message": message}), 200)


def get_team_members(team_id, user_id):
    """get team members who should receive this notification"""

    return (
        db.session.query(AppUser)
        .join(TeamMember.user)
        .filter(
            TeamMember.team_id == team_id,
            TeamMember.status == Statuses.ACTIVE,
            TeamMember.user_id != user_id,
            AppUser.fir_push_notif_token != None,
        )
        .all()
    )
