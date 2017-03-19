import os
import pytest
import sys
import unittest
from mock import patch

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except Exception:
    current_dir = os.getcwd()

sys.path.insert(0, os.path.join(current_dir, ".."))
sys.path.insert(0, os.path.join(current_dir, "..", "resources", "lib"))

import default

online = pytest.mark.skipif(
    not pytest.config.getoption("--online"),
    reason="online test"
)


class TestDefault(unittest.TestCase):

    @patch.object(sys, 'argv', ['plugin://plugin.video.afl-video/', '0', ''])
    @patch('index.make_list')
    def test_main_load_index(self, make_list):
        default.main()
        make_list.assert_called()

    @patch.object(sys, 'argv', ['plugin://plugin.video.afl-video/', '0', '?category=Match%20Replays%202017'])
    @patch('rounds.make_rounds')
    def test_main_make_rounds(self, make_rounds):
        default.main()
        make_rounds.assert_called_with('2017')

    @patch.object(sys, 'argv', ['plugin://plugin.video.afl-video/', '0', '?round_id=CD_R201710101'])
    @patch('matches.make_list')
    def test_main_make_matches_list(self, make_list):
        default.main()
        make_list.assert_called_with('CD_R201710101')

