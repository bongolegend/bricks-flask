import functools
from app.models import Exchange, AppUser
from app.base_init import init_app, init_db


def with_app_context(func):
    '''inits a new app and db, and runs func within it. used for functions run by scheduler'''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        app = init_app()
        db = init_db(app)
        kwargs['db'] = db
        with app.app_context():
            return func(*args, **kwargs)
    return wrapper


@with_app_context
def insert_exchange(router, user, inbound=None, **kwargs):
    '''log all elements of exchange to db'''
    db = kwargs['db']
        
    exchange = Exchange(
        router_id=router['router_id'],
        outbound=router['outbound'],
        inbound=inbound,
        actions=router['actions'],
        inbound_format=router['inbound_format'],
        confirmation=router['confirmation'],
        user_id=user['id'])
    print('LOGGED NEW EXCHANGE', exchange)

    db.session.add(exchange)
    db.session.commit()

    return exchange.to_dict()


@with_app_context
def update_exchange(session_exchange, next_exchange, **kwargs):
    '''update existing exchange row with inbound info and next router_id'''
    if session_exchange['id'] is not None:
        db = kwargs['db']
        
        queried_exchange = db.session.query(Exchange).filter_by(id=session_exchange['id']).one()
        queried_exchange.inbound = session_exchange['inbound']
        queried_exchange.next_router_id = next_exchange['router_id']
        queried_exchange.next_exchange_id = next_exchange['id']

        print('UPDATED EXISTING EXCHANGE', queried_exchange)

        db.session.add(queried_exchange)
        db.session.commit()

        return queried_exchange.to_dict()
    else:
        return None

