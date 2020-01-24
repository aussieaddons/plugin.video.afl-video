from __future__ import absolute_import, unicode_literals

import io
import json
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

from future.moves.urllib.parse import parse_qsl, unquote_plus, \
    urlencode, urlparse

import responses

import testtools

import resources.lib.config as config
from resources.tests.fakes import fakes


class IndexTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/LIVEMEDIA.json'), 'rb') as f:
            self.LIVEMEDIA_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/RESULTS2019.json'), 'rb') as f:
            self.RESULTS2019_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/RESULTS2020.json'), 'rb') as f:
            self.RESULTS2020_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/SEASONS.json'), 'rb') as f:
            self.SEASONS_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/VIDEO.json'), 'rb') as f:
            self.VIDEO_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/VIDEOS.json'), 'rb') as f:
            self.VIDEOS_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/xml/AFLW_BOX.xml'), 'rb') as f:
            self.AFLW_BOX_XML = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/xml/AFLW_BOX_LIVE.xml'), 'rb') as f:
            self.AFLW_BOX_LIVE_XML = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/xml/AFLW_INDEX.xml'), 'rb') as f:
            self.AFLW_INDEX_XML = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/xml/AFLW_LONG.xml'), 'rb') as f:
            self.AFLW_LONG_XML = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/xml/AFLW_SCORE.xml'), 'rb') as f:
            self.AFLW_SCORE_XML = io.BytesIO(f.read()).read()

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.afl-video/', '2', '', 'resume:false'])
    def test_make_list(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem
        mock_plugin = fakes.FakePlugin()
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.index as index
            index.make_list()
            for ind, category in enumerate(config.CATEGORIES):
                expected_url = 'plugin://{addonid}/?{params}'.format(
                    addonid='plugin.video.afl-video',
                    params=unquote_plus(urlencode({'category': category})))
                observed_url = mock_plugin.directory[ind].get('url')
                expected = urlparse(expected_url)
                observed = urlparse(observed_url)
                for x in range(6):
                    if x == 4:
                        self.assertEqual(dict(parse_qsl(expected[x])),
                                         dict(parse_qsl(observed[x])))
                    else:
                        self.assertEqual(expected[x], observed[x])

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.afl-video/', '2',
                 '?category=All%20Match%20Replays', 'resume:false'])
    @responses.activate
    def test_make_seasons_list(self, mock_listitem):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.GET, config.SEASONS_URL,
                      body=self.SEASONS_JSON, status=200)
        mock_listitem.side_effect = fakes.FakeListItem
        mock_plugin = fakes.FakePlugin()
        with mock.patch.dict('sys.modules', xbmcplugin=mock_plugin):
            import resources.lib.index as index
            index.make_seasons_list()
            expected_url = 'plugin://{addonid}/?{params}'.format(
                addonid='plugin.video.afl-video',
                params=unquote_plus(
                    urlencode({'season': 'CD_S2020014',
                               'current_round': 'CD_R202001401',
                               'name': 'AFL Premiership 2020'})))
            observed_url = mock_plugin.directory[0].get('url')
            expected = urlparse(expected_url)
            observed = urlparse(observed_url)
            for x in range(6):
                if x == 4:
                    self.assertEqual(dict(parse_qsl(expected[x])),
                                     dict(parse_qsl(observed[x])))
                else:
                    self.assertEqual(expected[x], observed[x])
