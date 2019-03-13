from flask import jsonify, request, make_response
from sqlalchemy import func, and_
import datetime as dt
import pytz
from app.models import AppUser, Task, Team, TeamMember
from app.actions.multiplayer import get_current_team_members_beta
from app import db
from app.constants import Statuses, TeamMemberTasks
from app.api.task import get_points_total

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
    get the following data:
        team:
            name
            id
            members:
                member:
                    username
                    id
                    memberid
                    tasks
    """

    if "TZ" not in request.headers:
        message = "Provide TZ in headers"
        return make_response(jsonify({"message": message}), 400)
    
    # get today in user's tz
    now = dt.datetime.now(tz=pytz.timezone(request.headers["TZ"]))
    today = dt.datetime(year=now.year, month=now.month, day=now.day)
    week_ago = today - dt.timedelta(days=7)

    team_data = query_team_data(user, week_ago)

    team_data = format_team_data(user, team_data)

    return make_response(jsonify(team_data), 200)


def query_team_data(current_user, lookback):

    # get teams the user is on
    teams = db.session.query(
        Team.name,
        Team.id.label("team_id")
    ).join(
        TeamMember.team
    ).filter(
        TeamMember.user_id == current_user.id,
        TeamMember.status == Statuses.ACTIVE
    ).subquery()
    # print("\nteams query: ", str(teams))

    # get members by team, non-distinct
    members = db.session.query(
        teams,
        TeamMember.id.label("member_id"),
        AppUser.id.label("user_id"),
        AppUser.username
    ).join(
        TeamMember,
        teams.c.team_id == TeamMember.team_id
    ).join(
        TeamMember.user
    ).subquery()

    # print("\nmembers query: ", str(members))

    tasks = db.session.query(
        Task.id.label("task_id"),
        Task.description,
        Task.due_date,
        Task.grade,
        Task.points_earned,
        Task.user_id
    ).filter(
        Task.active == True,
        Task.due_date >= lookback
    ).order_by(
        Task.due_date.desc()
    ).subquery()

    # combine members and tasks
    final_result = db.session.query(
        members,
        tasks.c.task_id,
        tasks.c.description,
        tasks.c.due_date,
        tasks.c.grade,
        tasks.c.points_earned
    ).outerjoin(
        tasks,
        members.c.user_id == tasks.c.user_id
    ).all()

    # print("FINAL QUERY: ", str(final_result))

    team_data = [dict(zip(TeamMemberTasks.KEYS, values)) for values in final_result]
    # print("TEAM DATA: ", team_data)
    return team_data


def format_team_data(current_user, task_list):
    """make data adhere to API format. do not add current user to the member_tasks list"""
    
    # sort tasks by member
    member_dict = dict()
    for task in task_list:
        member_id = task["member_id"]

        if member_id not in member_dict.keys():
            member_dict[member_id] = { "tasks": list() }

        # move values out of task and into member
        member_dict[member_id]["username"] = task.pop("username")
        member_dict[member_id]["user_id"] = task.pop("user_id")
        member_dict[member_id]["member_id"] = task.pop("member_id")
        member_dict[member_id]["points_total"] = get_points_total(member_dict[member_id]["user_id"])
        member_dict[member_id]["name"] = task.pop("name")
        member_dict[member_id]["team_id"] = task.pop("team_id")
        
        if task["task_id"] is not None:
            member_dict[member_id]["tasks"].append(task)
    
    member_list = member_dict.values()

    # sort members by team
    team_dict = dict()

    for member in member_list:
        team_id = member["team_id"]
        # add entries for new teams
        if team_id not in team_dict.keys():
            team_dict[team_id] = { "members": list() }
        
        team_dict[team_id]["name"] = member.pop("name")
        team_dict[team_id]["team_id"] = member.pop("team_id")

        team_dict[team_id]["members"].append(member)
    
    team_list = team_dict.values()
    print("RETURN OBJECT: ", team_list)
    return team_list


