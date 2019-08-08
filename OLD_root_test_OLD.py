"""run tests from here"""
import unittest
from tests.chatbot.test_all_routers import TestAllRouters
from tests.chatbot.test_invitation import TestInitOnboardingInvited
from tests.chatbot.tools import generate_tests_for_class

if __name__ == "__main__":
    generate_tests_for_class(TestAllRouters)
    generate_tests_for_class(TestInitOnboardingInvited)

    loader = unittest.TestLoader()
    tests = loader.discover(".")

    runner = unittest.TextTestRunner(warnings="ignore")
    runner.run(tests)
