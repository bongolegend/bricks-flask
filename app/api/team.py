from flask import jsonify, request, make_response
from sqlalchemy import func, and_
import datetime as dt
import pytz
from app.models import AppUser, Task, Team, TeamMember
from app.actions.multiplayer import get_current_team_members_beta
from app import db
from app.constants import Statuses, Tasks

def main(user):
    if request.method == "PUT":
        return put(user)
    if request.method == "GET":
        return get(user)
    else:
        raise Exception


def put(user):
    """Save a new team to the db"""

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
    """
    get most recent tasks for your friends and yourself.
    """

    if "TZ" not in request.headers:
        message = "Provide TZ in headers"
        return make_response(jsonify({"message": message}), 400)
    
    # get today in user's tz
    now = dt.datetime.now(tz=pytz.timezone(request.headers["TZ"]))
    today = dt.datetime(year=now.year, month=now.month, day=now.day)

    team_data = query_team_data(user, today)

    team_data = format_team_data(user, team_data)

    return make_response(jsonify(team_data), 200)


def query_team_data(current_user, today):

    # get teams the user is on
    teams = db.session.query(
        Team.name.label("team_name"), 
        Team.id.label("team_id")
    ).join(
        TeamMember.team
    ).filter(
        TeamMember.user_id == current_user.id,
        TeamMember.status == Statuses.ACTIVE
    ).subquery().alias("teams")
    # print("\nteams query: ", str(teams))

    # get members by team, non-distinct
    members_query = db.session.query(
        teams.c.team_id, 
        teams.c.team_name,
        TeamMember.id.label("member_id"),
        AppUser.username,
        AppUser.id.label("user_id")
    ).join(
        TeamMember,
        teams.c.team_id == TeamMember.team_id
    ).join(
        TeamMember.user
    )

    members = members_query.subquery()
    members_data = members_query.all()
    user_ids = [member.user_id for member in members_data]

    # print("\nmembers query: ", str(members))
    # print("\nmembers data: ", str(members_data))
    
    # get all latest due dates
    due_dates = db.session.query(
        func.max(Task.due_date).label("due_date"), 
        Task.user_id, 
    ).filter(
        Task.active == True,
        Task.user_id.in_(user_ids),
        Task.due_date >= today 
    ).group_by(Task.user_id).subquery()

    # print("\ndue dates query: ", str(due_dates))

    tasks = db.session.query(
        Task.user_id,
        Task.id.label("task_id"),
        Task.due_date,
        Task.description,
        Task.grade,
        Task.points_earned,
        Task.points_total
    ).join(
        due_dates,
        and_(
            Task.due_date == due_dates.c.due_date,
            Task.user_id == due_dates.c.user_id
    )).filter(
        Task.active == True
    ).subquery()

    # print("\ntasks query: ", str(tasks))


    # join tasks to team members
    complete_query = db.session.query(
        members.c.username,
        members.c.user_id, 
        members.c.member_id,

        members.c.team_name, 
        members.c.team_id, 
        
        tasks.c.task_id,
        tasks.c.due_date,
        tasks.c.description,
        tasks.c.grade,
        tasks.c.points_earned,
        tasks.c.points_total
        ).outerjoin(
            tasks,
            members.c.user_id == tasks.c.user_id
        ).all()
    


    team_data = [dict(zip(Tasks.KEYS, values)) for values in complete_query]
    # print("TEAM DATA: ", team_data)
    return team_data


def format_team_data(current_user, team_data):
    """make data adhere to API format. do not add current user to the member_tasks list"""

    teams_dict = dict()

    for member_task in team_data:
        team_id = member_task["team_id"]
        # add entries for new teams
        if team_id not in teams_dict.keys():
            teams_dict[team_id] = dict(
                team_name=member_task["team_name"],
                team_id=team_id,
                member_tasks=list()
            )

        if member_task["user_id"] != current_user.id:
            teams_dict[team_id]["member_tasks"].append(member_task)
    
    return_object = teams_dict.values()
    # print("RETURN OBJECT: ", return_object)
    return return_object


