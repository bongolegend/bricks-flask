import functools
from app.models import Exchange, User
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
def update_exchange(exchange_id, inbound, next_router_id, **kwargs):
    '''update existing exchange row with inbound info and next router_id'''
    if exchange_id is not None:
        db = kwargs['db']
        
        exchange = db.session.query(Exchange).filter_by(id=exchange_id).one()
        exchange.inbound = inbound
        exchange.next_router_id = next_router_id
        print('UPDATED EXISTING EXCHANGE', exchange)

        db.session.add(exchange)
        db.session.commit()

        return exchange.to_dict()
    else:
        return None

