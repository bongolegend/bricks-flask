'''run tests from here'''
import unittest
from app.models import Exchange
from tests.test_all_routers import TestAllRouters
from tests.test_notifications import TestNotifications
from tests.test_invitation import TestInitOnboardingInvited
from tests.actions.test_multiplayer import TestMultiplayer


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
        response = self.client.post('/sms', data=dict(Body=inbound, From=self.mitch.phone_number))

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


if __name__ == '__main__':
    generate_tests_for_class(TestAllRouters)
    generate_tests_for_class(TestInitOnboardingInvited)

    unittest.main(warnings='ignore')    