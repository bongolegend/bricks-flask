from app.base_init import init_app, init_db
import unittest
from app.models import Exchange

def with_app_context(func):
    '''inits a new app and db, and runs func within it. used for functions run by scheduler. useful for tests tho'''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        app = init_app()
        db = init_db(app)
        kwargs['db'] = db
        with app.app_context():
            return func(*args, **kwargs)
    return wrapper


def generator(router, inbound=str()):
    '''function that returns one test function per router'''
    def test(self):
        print(f"""
=============================
TESTING ROUTER: {router.__name__}
TESTING INBOUND: {inbound}
=============================
        """)
        exchange = Exchange(router=router.__name__, user=self.mitch)
        self.db.session.add(exchange)
        response = self.client.post('/chat', data=dict(Body=inbound, From=self.mitch.phone_number))

    return test


def generate_tests_for_class(test_class):
    '''For a given test class, generate all of its tests'''
    for name, router in test_class.get_routers().items():
        if isinstance(router.inbound_format, dict):
            for inbound in router.inbound_format:
                test_name = f'test_{name}_{inbound}'
                test = generator(router,  inbound)
                setattr(test_class, test_name, test)
        else:
            test_name = f"test_{name}"
            test = generator(router)
            setattr(test_class, test_name, test)