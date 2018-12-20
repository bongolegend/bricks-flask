'''Functions that support the main conversations module'''
from flask import current_app
from twilio.rest import Client
from app import db
from app.models import Exchange, AppUser






def query_user_with_number(phone_number):
    '''
    use phone number to find user in db, else add to db
    returns the user object
    '''

    user = db.session.query(AppUser).filter_by(phone_number=phone_number).first()

    if user is not None:
        return user.to_dict()
    else:
        new_user = AppUser(phone_number=phone_number)
        db.session.add(new_user)
        db.session.commit()
        return new_user.to_dict()


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


def insert_exchange(router, user, inbound=None, **kwargs):
    '''log all elements of exchange to db'''
        
    exchange = Exchange(
        router=router.name,
        outbound=router.outbound,
        inbound=inbound,
        confirmation=router.confirmation,
        user_id=user['id'])
    print('INSERTED NEW EXCHANGE', exchange)

    db.session.add(exchange)
    db.session.commit()

    return exchange.to_dict()


def update_exchange(current_exchange, next_exchange, inbound, **kwargs):
    '''update existing exchange row with inbound info and next router name'''
    if current_exchange is not None:
        queried_exchange = db.session.query(Exchange).filter_by(id=current_exchange['id']).one()
        queried_exchange.inbound = inbound,
        queried_exchange.next_router = next_exchange['router'],
        queried_exchange.next_exchange_id = next_exchange['id']

        print('UPDATED EXISTING EXCHANGE', queried_exchange)

        db.session.add(queried_exchange)
        db.session.commit()

        return queried_exchange.to_dict()
    else:
        return None


def send_message(user, outbound):
    '''send outbound to user with twilio'''

    account_sid = current_app.config['TWILIO_ACCOUNT_SID']
    auth_token = current_app.config['TWILIO_AUTH_TOKEN']
    from_number = current_app.config['TWILIO_PHONE_NUMBER']

    client = Client(account_sid, auth_token)

    message = client.messages.create(from_=from_number,
        to=user['phone_number'],
        body=outbound)
    
    print(f"MESSAGE SENT TO {user['username']}: {outbound}")

    return message