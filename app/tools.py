import functools
from app.models import Exchange
from app.base_init import init_app, init_db
from app.routers_and_outbounds import outbound_df


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
def insert_exchange(router_id, user, inbound=None, **kwargs):
    '''log all elements of exchange to db'''
    db = kwargs.get('db')
    assert db is not None, 'You must provide a db instance'

    router = outbound_df[outbound_df.router_id == router_id].iloc[0]
        
    exchange = Exchange(
        router_id=router.router_id,
        outbound=router.outbound,
        inbound=inbound,
        actions=router.actions,
        inbound_format=router.inbound_format,
        confirmation=router.confirmation,
        user_id=user['id'])
    print('LOGGED NEW EXCHANGE', exchange)

    db.session.add(exchange)
    db.session.commit()

    return exchange.to_dict()

@with_app_context
def update_exchange(exchange_id, inbound, next_router_id, **kwargs):
    '''update existing exchange row with inbound info and next router_id'''
    db = kwargs.get('db')
    assert db is not None, 'You must provide a db instance'
    
    exchange = db.session.query(Exchange).filter_by(id=exchange_id).one()
    exchange.inbound = inbound
    print('UPDATED EXISTING EXCHANGE', exchange)

    db.session.add(exchange)
    db.session.commit()

    return exchange.to_dict()




MULTIPLE_CHOICE = {
    'yes': ['yes', 'y', 'ye', 'ya', 'yea', 'yep', 'yup', 'yeah'],
    'no': ['no', 'n', 'na', 'nope'],
    'a': ['a', 'a)'],
    'b': ['b', 'b)'],
    'c': ['c', 'c)'],
    'd': ['d', 'd)'],
}

def parse_multiple_choice(inbound):
    inbound = inbound.lower()
    for term, matches in MULTIPLE_CHOICE.items():
        if inbound in matches:
            return term
    raise NotImplementedError('Nothing in the dictionary matches.')


def parse_inbound(inbound, router_id):

    inbound_format = outbound_df[outbound_df.router_id == router_id].inbound_format.iloc[0]
    if inbound_format == '*':
        return inbound
    elif inbound_format == 'multiple_choice':
        return parse_multiple_choice(inbound)
    else:
        raise NotImplementedError(f'The inbound format {inbound_format} does not have a parser.')