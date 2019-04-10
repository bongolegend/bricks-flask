from flask import jsonify, request, make_response
from app.models import AppUser, TeamMember
from app import db
from app.push import notify_user, send_message_notif
from app.constants import Statuses


def post(user):
    """send a push notification containing a new message to the user"""

    data = request.get_json()

    team_id = data["team_id"]
    content = data["content"]

    # get team members for this team
    team_members = db.session.query(AppUser).join(
        TeamMember.user
    ).filter(
        TeamMember.team_id == team_id,
        TeamMember.status == Statuses.ACTIVE,
        TeamMember.user_id != user.id,
        AppUser.fir_push_notif_token != None
    ).all()

    for member in team_members:
        if member.chat_notifs:
            send_message_notif(member.fir_push_notif_token, 1, title=user.username, body=content)
        else:
            send_message_notif(member.fir_push_notif_token, 1)

    message = "Data notifications sent to team members"
    return make_response(jsonify({"message": message}), 200)
