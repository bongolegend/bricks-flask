from app import db
from app.models import AppUser, Exchange


def main(session, request):
    '''identify the user and start the session'''
    if 'user' not in session:
        session['user'] = query_user(request.values.get('From')).to_dict()
        print('\n')
        print(f'SESSION STARTED FOR {session["user"]["username"]}')

    if 'exchange' not in session:
        last_exchange = query_last_exchange(session['user'])

        if last_exchange is not None: # handles returning users
            session['exchange'] = last_exchange
            if session['exchange']['actions'] is None:
                session['exchange']['actions'] = tuple()

            # print('CURRENT EXCHANGE WAS ', session['exchange']['router_id'])
        else: # initiate new exchange
            session['exchange'] = dict()
            session['exchange']['router_id'] = 'init_onboarding'
            session['exchange']['actions'] = tuple()
            session['exchange']['id'] = None
            session['exchange']['confirmation'] = None


def query_user(phone_number):
    '''
    use phone number to find user in db, else add to db
    returns the user object
    '''

    user = db.session.query(AppUser).filter_by(phone_number=phone_number).first()

    if user is not None:
        return user
    else:
        new_user = AppUser(phone_number=phone_number)
        db.session.add(new_user)
        db.session.commit()
        return new_user


def query_last_exchange(user):
    '''find the last exchange in the db for this user'''
    last_exchange = db.session.query(Exchange)\
        .filter_by(user_id=user['id'])\
        .order_by(Exchange.created.desc())\
        .first()
    
    if last_exchange is None:
        return None
    else:
        return last_exchange.to_dict()