'''run tests from here'''
import unittest
from tests.test_all_routers import TestAllRouters, generator, get_router
from tests.test_notifications import TestNotifications


if __name__ == '__main__':
    for name, router in get_router().items():
        if isinstance(router.inbound_format, dict):
            for inbound in router.inbound_format:
                test_name = f'test_{name}_{inbound}'
                test = generator(router, inbound)
                setattr(TestAllRouters, test_name, test)
        else:
            test_name = f"test_{name}"
            test = generator(router)
            setattr(TestAllRouters, test_name, test)

    unittest.main(warnings='ignore')    