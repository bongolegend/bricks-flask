from sqlalchemy import func
from app import db
from app.models import AppUser, Point, Exchange, Team, TeamMember
from app.constants import Statuses
from app import tools


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
    invited_user = tools.query_user_with_number(phone_number)
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

    exchange = tools.query_last_exchange(invited_user)
    if exchange is None:
        router = init_onboarding_invited()
    else:
        router = you_were_invited()

    results = router.run_pre_actions(
        user=invited_user,
        exchange=exchange,
        invited_by=user)

    router.outbound = router.outbound.format(**results)

    tools.notify(invited_user, router)


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

    tools.notify_(inviter.to_dict(), outbound)


def confirm_team_member(user, **kwargs):
    '''look up which membership was just accepted, and set it to confirmed'''
    membership = db.session.query(TeamMember).filter(
        TeamMember.user_id == user['id'],
        TeamMember.status == Statuses.PENDING)\
        .order_by(TeamMember.created.desc()).first()
    
    membership.status = Statuses.CONFIRMED
    db.session.commit()

    print("TEAM MEMBER CONFIRMED: ", user['username'])


def query_team_members(user):
    '''get the team members for this user. exclude this user from the results.'''
    team_ids = db.session.query(Team.id).join(TeamMember)\
                .filter(TeamMember.user_id == user['id'])

    team_members = db.session.query(AppUser).join(TeamMember.user)\
        .filter(
            TeamMember.team_id.in_(team_ids),
            TeamMember.user_id != user['id']).all()

    return team_members