import os
import pytest
import requests_mock
import sys
import unittest
from mock import patch

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except Exception:
    current_dir = os.getcwd()

sys.path.insert(0, os.path.join(current_dir, ".."))
sys.path.insert(0, os.path.join(current_dir, "..", "resources", "lib"))

import comm

online = pytest.mark.skipif(
    not pytest.config.getoption("--online"),
    reason="online test"
)

@requests_mock.mock()
class TestComm(unittest.TestCase):

    def test_comm_fetch_url(self, m):
        m.get('http://testurl.com', text='return_output')
        self.assertEqual(comm.fetch_url('http://testurl.com'), 'return_output')
