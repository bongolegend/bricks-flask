from flask import jsonify, request, make_response
from sqlalchemy import func, and_
import datetime as dt
import pytz
from app.models import AppUser, Task, Team, TeamMember
from app.actions.multiplayer import get_current_team_members_beta
from app import db
from app.constants import Statuses, Tasks

def get(user):
    """
    get most recent tasks for your friends and yourself. return data format:

    [
        {
            name:
            id:
            members: [
                {
                    username:
                    user_id:
                    task_description:
                    task_id:
                    due_date:
                    grade:
                }, 
                {...}
            ]
        }
    ]
    """

    if "TZ" not in request.headers:
        message = "Provide TZ in headers"
        return make_response(jsonify({"message": message}), 400)
    
    # get today in user's tz
    now = dt.datetime.now(tz=pytz.timezone(request.headers["TZ"]))
    today = dt.datetime(year=now.year, month=now.month, day=now.day)

    team_data = query_team_data(user, today)

    team_data = format_team_data(team_data)
    # print(team_data)

    return make_response(jsonify(team_data), 200)


def query_team_data(user, today):

    # get teams the user is on
    teams = db.session.query(
        Team.name.label("team_name"), 
        Team.id.label("team_id")
    ).join(
        TeamMember.team
    ).filter(
        TeamMember.user_id == user.id,
        TeamMember.status == Statuses.ACTIVE
    ).subquery()

    # print("\nteams query: ", str(teams))


    # get members by team, non-distinct
    members_query = db.session.query(
        TeamMember.user_id,
        TeamMember.id.label("member_id"), 
        teams.c.team_id, 
        teams.c.team_name,
        AppUser.username
    ).join(
        teams,
        TeamMember.team_id == teams.c.team_id
    ).join(
        TeamMember.user
    ).filter(
        TeamMember.user != user # exclude this user
    )

    members = members_query.subquery()
    members_data = members_query.all()
    user_ids = [user.user_id for user in members_data]

    # print("\nmembers query: ", str(members))

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
    return team_data


def format_team_data(team_data):
    """make data adhere to API format"""

    teams_dict = dict()

    for user in team_data:
        team_id = user["team_id"]
        # add entries for new teams
        if team_id not in teams_dict.keys():
            teams_dict[team_id] = dict(
                team_name=user["team_name"],
                team_id=team_id,
                member_tasks=list()
            )

        # user.pop("team_name")
        # user.pop("team_id")
        
        teams_dict[team_id]["member_tasks"].append(user)
    
    return teams_dict.values()



