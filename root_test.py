'''run tests from here'''
import unittest
from app.models import Exchange
from tests.test_all_routers import TestAllRouters
from tests.test_invitation import TestInitOnboardingInvited
from tests.tools import generate_tests_for_class

if __name__ == '__main__':
    generate_tests_for_class(TestAllRouters)
    generate_tests_for_class(TestInitOnboardingInvited)

    loader = unittest.TestLoader()
    tests = loader.discover('.')

    runner = unittest.TextTestRunner(warnings='ignore')
    runner.run(tests)