import os
from tests.config_test import BaseTestCase


class TestChat(BaseTestCase):

    def test_no_inbound(self):
        '''test that if no inbound is provided, there is no error'''
        self.client.post('/sms')

 