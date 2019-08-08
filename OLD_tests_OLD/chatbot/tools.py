import logging
from app.models import Exchange


def generator(router, inbound=str()):
    """function that returns one test function per router"""

    def test(self):
        logging.info(f"Test for: {router.__name__}")
        exchange = Exchange(router=router.__name__, user=self.mitch)
        self.db.session.add(exchange)
        self.client.post("/chat", data=dict(Body=inbound, From=self.mitch.phone_number))

    return test


def generate_tests_for_class(test_class):
    """For a given test class, generate all of its tests"""
    for name, router in test_class.get_routers().items():
        if isinstance(router.inbound_format, (dict, tuple)):
            for inbound in router.inbound_format:
                test_name = f"test_{name}_{inbound}"
                test = generator(router, inbound)
                setattr(test_class, test_name, test)
        else:
            test_name = f"test_{name}"
            test = generator(router)
            setattr(test_class, test_name, test)
