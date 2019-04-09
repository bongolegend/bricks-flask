from flask import jsonify, request, make_response
from app.models import AppUser, TeamMember
from app import db
from app.push import notify_user

def post(user):
    """send a push notification to nudge the user"""

    data = request.get_json()

    nudgee_id = data["nudgee"]

    nudgee = db.session.query(AppUser.fir_push_notif_token, AppUser.username).join(
        TeamMember.user
    ).filter(
        TeamMember.id == nudgee_id
    ).one()
    if nudgee.fir_push_notif_token is not None:
        title = f"Nudge from {user.username}"
        body = "Choose your top task!"
        notify_user(nudgee.fir_push_notif_token, title, body)

        message = f"Nudge sent to {nudgee.username}"
        return make_response(jsonify({"message": message}), 200)
    else:
        message = "User cannot receive push notifications"
        return make_response(jsonify({"message": message}), 400)
