from sqlalchemy import func
from app import db
from app.models import AppUser, Point, Exchange, Team, TeamMember
from app.constants import Statuses, Reserved
from app import tools


def get_leaderboard(**kwargs):
    '''Make a leaderboard across all users, returning the top users'''
    users = db.session.query(AppUser.username, func.sum(Point.value))\
        .join(Point)\
        .group_by(AppUser.username)\
        .order_by(func.sum(Point.value).desc())\
        .limit(10)\
        .all()
    
    board = "{points:<8}{username}\n".format(username='USERNAME', points='POINTS')
    for user, value in users:
        board = board + "{value:<15}{user}\n".format(user=user[:16], value=value)

    return board


def insert_team(user, inbound, **kwargs):
    '''Create a new team with the user as the founder, and the inbound as the team name. 
     add this user to this team in TeamMember'''
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
    teams = db.session.query(Team.id, Team.name).join(TeamMember)\
        .filter(TeamMember.user_id == user['id']).all()

    if teams:
        team_list = str()
        for team_id, name in teams:
            team_list += f"{team_id}: {name}\n"
        return team_list
    else:
        return "You have no teams. Return to the main menu and create one."


def insert_member(user, inbound, init_onboarding_invited, you_were_invited, **kwargs):
    '''Add member to the given team as PENDING. 
    Inbound should already be parsed as tuple(team_id, phone_number_str)'''

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
    if exchange is None or invited_user.username == Reserved.NEW_USER:
        router = init_onboarding_invited()
    else:
        router = you_were_invited()

    results = router.run_pre_actions(
        user=invited_user,
        exchange=exchange,
        invited_by=user)

    router.outbound = router.outbound.format(**results)

    tools.send_message(invited_user, router.outbound)

    # record the fact that this invitation was sent to a user
    tools.insert_exchange(router, invited_user)


def get_last_invitation(user, **kwargs):
    '''find the most recent invitation for user'''
    inviter_username, inviter_phone_number, team_name = db.session.query(AppUser.username, AppUser.phone_number, Team.name)\
        .join(TeamMember.invited_by, TeamMember.team)\
        .filter(
            TeamMember.user_id == user['id'],
            TeamMember.status == Statuses.PENDING)\
        .order_by(TeamMember.created.desc()).first()

    return inviter_username, team_name, inviter_phone_number

# TODO(Nico) create this 
def intro_to_team(**kwargs):
    return "Me, You and Larry"


def notify_inviter(user, membership, **kwargs):
    '''look up which membership was just responded to, and notify the inviter'''
    # find the inviter
    inviter, team_name = db.session.query(AppUser, Team.name)\
        .join(TeamMember.invited_by, TeamMember.team).filter(
            TeamMember.user_id == user['id'],
            TeamMember.invited_by_id == membership.invited_by_id,
            TeamMember.team_id == membership.team_id)\
        .order_by(TeamMember.updated.desc()).first()

    if membership.status == Statuses.ACTIVE:    
        outbound = "Your friend @{phone_number} just accepted your invitation to {team_name}."
    elif membership.status == Statuses.REJECTED:
        outbound = "Your friend @{phone_number} did not accept your invitation to {team_name}."
    elif membership.status == Statuses.PENDING: 
        return None
    
    outbound = outbound.format(phone_number=user['phone_number'], team_name=team_name)

    tools.send_message(inviter.to_dict(), outbound)


def respond_to_invite(user, inbound, **kwargs):
    '''look up which membership was just accepted, and set it to confirmed'''
    membership = db.session.query(TeamMember).filter(
        TeamMember.user_id == user['id'],
        TeamMember.status == Statuses.PENDING)\
        .order_by(TeamMember.created.desc()).first()

    assert membership is not None
    
    if inbound == 'a':
        membership.status = Statuses.ACTIVE
        print("INVITATION CONFIRMED: ", user['phone_number'])
    elif inbound == 'b':
        membership.status = Statuses.REJECTED
        print("INVITATION REJECTED BY: ", user['phone_number'])
    else:
        print('INVITEE IS TRYING TO UNDERSTAND INVITATION.')
    db.session.commit()

    return membership


def get_team_members(user):
    '''get the team members for this user. exclude this user from the results.'''
    team_ids = db.session.query(Team.id).join(TeamMember)\
                .filter(TeamMember.user_id == user['id'])

    team_members = db.session.query(AppUser, Team).join(TeamMember.user, TeamMember.team)\
        .filter(
            TeamMember.team_id.in_(team_ids),
            TeamMember.user_id != user['id'],
            TeamMember.status == Statuses.ACTIVE).all()

    return team_members


def notify_team_members(user, inbound):
    '''Send message to teammembers that user is doing inbound'''

    team_members = get_team_members(user)
    for team_member, team in team_members:
        outbound = f"Your friend {user['username']} is gonna do this: {inbound}."
        tools.send_message(team_member.to_dict(), outbound)


def get_phonenumber(user, **kwargs):
    inviter_username, team_name, inviter_phone_number = get_last_invitation(user)

    return inviter_phone_number


def view_team_members(user, **kwargs):
    '''list all teams and corresponding members for user'''
    team_members = get_team_members(user)
    teams = dict()
    for member, team in team_members:
        if not  team.name in teams:
            teams[team.name] = str()
        teams[team.name] += f"\n- {member.username}"
    
    all_teams = str()
    for key, value in teams.items():
        all_teams += "\n" + key + value 
    
    return all_teams

