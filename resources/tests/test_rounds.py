from __future__ import absolute_import, unicode_literals

import io
import json
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

import responses

import testtools

import resources.lib.config as config
from resources.tests.fakes import fakes


class RoundsTests(testtools.TestCase):
    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/SEASONS.json'), 'rb') as f:
            self.SEASONS_JSON = io.BytesIO(f.read()).read()

    @responses.activate
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.afl-video/',
                 '2',
                 '?current_round=CD_R202001401&name=2020%20Toyota%20AFL'
                 '%20Premiership&season=CD_S2020014'])
    def test_make_rounds(self, mock_listitem):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.GET, config.SEASONS_URL,
                      body=self.SEASONS_JSON, status=200)
        mock_listitem.side_effect = fakes.FakeListItem
        mock_plugin = fakes.FakePlugin()
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.rounds as rounds
            rounds.make_rounds({'season': 'CD_S2020014'})
            self.assertEqual(23, len(mock_plugin.directory))
