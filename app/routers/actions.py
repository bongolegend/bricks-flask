import datetime as dt
import pytz
from sqlalchemy import func
from app import db
from app.models import AppUser, Notification, Point, Exchange, Task, Team, TeamMember
from app.constants import Statuses, US_TIMEZONES
from app.queries import query_user, query_last_exchange, query_team_members
from app import queries
    

def insert_notifications(user, choose_task, morning_confirmation, did_you_do_it, **kwargs):
    '''Create two morning and one evening notif. Add notif to db. pass the input classes as instances'''

    # find existing notifications
    existing_choose_tasks = Notification.query.filter_by(
        user_id=user['id'], router=choose_task.__name__).all()
    existing_morning_confimations = Notification.query.filter_by(
        user_id=user['id'], router=morning_confirmation.__name__).all()
    existing_evening_checkins = Notification.query.filter_by(
        user_id=user['id'], router=did_you_do_it.__name__).all()
    
    if not existing_choose_tasks:
        notif = Notification(
            router=choose_task.__name__,
            body=choose_task.outbound,
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            active=True,
            user_id=user['id'])
        db.session.add(notif)
    
    if not existing_morning_confimations:
        notif = Notification(
            router=morning_confirmation.__name__,
            body=morning_confirmation.outbound,
            day_of_week='mon-fri',
            hour=8,
            minute=0,
            active=True,
            user_id=user['id'])
        db.session.add(notif)

    if not existing_evening_checkins:
        notif = Notification(
            router=did_you_do_it.__name__,
            body=did_you_do_it.outbound,
            day_of_week='mon-fri',
            hour=21,
            minute=0,
            active=True,
            user_id=user['id'])
        db.session.add(notif)

    db.session.commit()


def update_timezone(inbound, user, **kwargs):
    tz = US_TIMEZONES.get(inbound, None)
    if tz is not None:        
        user_obj = db.session.query(AppUser).filter_by(id=user['id']).one()
        user_obj.timezone = tz
        user['timezone'] = tz
            
        db.session.commit()

    else:
        raise ValueError('INVALID TIMEZONE CHOICE')

    return tz


def update_username(inbound, user, **kwargs):
    user_obj = db.session.query(AppUser).filter_by(id=user['id']).one()
    user_obj.username = inbound
    user['username'] = inbound
    db.session.commit()


def insert_points(user, value, **kwargs):
    point = Point(value=value, user_id=user['id'])
    db.session.add(point)
    db.session.commit()


def query_points(user, **kwargs):
    points = db.session.query(func.sum(Point.value).label('points')).filter(Point.user_id == user['id']).one()[0]

    if points is None:
        return 0
    else:
        return points


def query_latest_task(user, choose_task, choose_tomorrow_task, **kwargs):
    '''query the latest task'''
    task = db.session.query(Task).filter(
        Task.user_id == user['id'],
        Task.active == True
        ).order_by(Task.due_date.desc()).first()

    return task.description


def insert_task(user, exchange, inbound, choose_task, choose_tomorrow_task, did_you_do_it, **kwargs):
    '''
    insert task based on input, and set all other tasks with the same due date to inactive.
    If the user has team mates, send them a notification of this task.
    '''

    # what day is it for user?
    today_local = dt.datetime.now(tz=pytz.timezone(user['timezone']))

    # what time today are your tasks due? look at the Notif did_you_do_it
    hour, minute = db.session.query(Notification.hour, Notification.minute).filter(
        Notification.user_id == user['id'],
        Notification.router == did_you_do_it.__name__,
        Notification.active == True).one()

    # local time that task is due
    due_today_local = today_local.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # convert due_today to utc, then make timezone naive
    due_today = due_today_local.astimezone(pytz.utc).replace(tzinfo=None)

    # determine the due date based on the router id
    if exchange['router'] == choose_task.__name__:
        due_date = due_today
    elif exchange['router'] == choose_tomorrow_task.__name__:
        due_date = due_today + dt.timedelta(days=1)
    else:
        raise NotImplementedError(f"The router {exchange['router']} is not valid for inserting tasks.")

    # create a new task
    new_task = Task(
        description = inbound,
        due_date = due_date,
        active = True,
        exchange_id = exchange['id'],
        user_id = user['id'])
    
    # set any tasks that are already for that day to inactive
    existing_tasks = db.session.query(Task).filter(
        Task.due_date == due_date,
        Task.user_id == user['id'],
    ).all()

    for existing_task in existing_tasks:
        existing_task.active = False
    
    db.session.add(new_task)
    db.session.commit()

    # notify team members of this task
    team_members = query_team_members(user)
    for team_member in team_members:
        outbound = f"Your friend {user['username']} is gonna do this: {inbound}."
        queries.notify_(team_member.to_dict(), outbound)


def leaderboard(**kwargs):
    '''Make a leaderboard across all users, returning the top 5'''
    users = db.session.query(AppUser.username, func.sum(Point.value))\
        .join(Point)\
        .group_by(AppUser.username)\
        .order_by(func.sum(Point.value).desc())\
        .limit(10)\
        .all()
    
    leaderboard = "{username:_<12}{points}\n".format(username='USERNAME', points='POINTS')
    for user, value in users:
        leaderboard = leaderboard + "{user:_<20}{value}\n".format(user=user[:16], value=value)

    return leaderboard


def insert_team(user, inbound, **kwargs):
    '''Create a new team with the user as the founder, and the inbound as the team name. Automatically add user to this team'''
    team = Team(founder_id=user['id'], name=inbound)

    member = TeamMember(
        user_id=user['id'],
        team=team,
        invited_by_id=user['id'],
        status=Statuses.ACTIVE)

    db.session.add(team)
    db.session.add(member)
    db.session.commit()

    print(f"USER {user['username']} CREATED TEAM {team.name}")


def list_teams(user, **kwargs):
    '''List the teams that user is a member of'''
    teams = db.session.query(Team.id, Team.name).join(TeamMember).filter(TeamMember.user_id == user['id']).all()

    if teams:
        team_list = str()
        for team_id, name in teams:
            team_list += f"{team_id}: {name}\n"
        return team_list
    else:
        return "You have no teams. Return to the main menu and create one."


def insert_member(user, inbound, init_onboarding_invited, you_were_invited, **kwargs):
    '''Add member to the given team as a PENDING member. Inbound should be parsed as (team_id, phone_number_str)'''

    team_id, phone_number = inbound

    # confirm that user is part of team
    team = db.session.query(Team).join(TeamMember).filter(
        Team.id == team_id, 
        TeamMember.user_id == user['id']
    ).one()

    if not team:
        return None

    # lookup the phone-number, add if not already a user
    invited_user = query_user(phone_number)
    # TODO(Nico) you will need to ask this person for their user name and tz

    # insert invitee into db
    invited_member = TeamMember(
        user_id = invited_user['id'],
        team_id = team_id,
        invited_by_id = user['id'],
        status = Statuses.PENDING)
    
    db.session.add(invited_member)
    db.session.commit()

    # send invitation to invitee
    # you need to get the right router
    # you should trigger a new router, but does that

    exchange = query_last_exchange(invited_user)
    if exchange is None:
        router = init_onboarding_invited()
    else:
        router = you_were_invited()

    results = router.run_pre_actions(
        user=invited_user,
        exchange=exchange,
        invited_by=user)

    router.outbound = router.outbound.format(**results)

    queries.notify(invited_user, router)


def query_last_invitation(user, **kwargs):
    '''find the most recent invitation for user'''
    inviter, team = db.session.query(AppUser.username, Team.name)\
        .join(TeamMember.invited_by, TeamMember.team)\
        .filter(
            TeamMember.user_id == user['id'],
            TeamMember.status == Statuses.PENDING)\
        .order_by(TeamMember.created.desc()).first()

    return inviter, team


def intro_to_team(**kwargs):
    return "Me, You and Larry"


def confirm_team_member(user, **kwargs):
    '''look up which membership was just accepted, and set it to confirmed'''
    membership = db.session.query(TeamMember).filter(
        TeamMember.user_id == user['id'],
        TeamMember.status == Statuses.PENDING)\
        .order_by(TeamMember.created.desc()).first()
    
    membership.status = Statuses.CONFIRMED
    db.session.commit()

    print("TEAM MEMBER CONFIRMED: ", user['username'])


def notify_inviter(user, inbound, **kwargs):
    '''look up which membership was just responded to, and notify the inviter'''
    # find the inviter
    inviter, team_name = db.session.query(AppUser, Team.name).join(TeamMember.invited_by, TeamMember.team).filter(
        TeamMember.user_id == user['id'],
        TeamMember.status == Statuses.CONFIRMED)\
        .order_by(TeamMember.updated.desc()).first()

    if inbound == 'yes':    
        outbound = "Your friend {username} just accepted your invitation to {team_name}."
    else:
        outbound = "Your friend {username} did not accept your invitation to {team_name}."
    
    outbound = outbound.format(username=user['username'], team_name=team_name)

    queries.notify_(inviter.to_dict(), outbound)
