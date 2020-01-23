from __future__ import absolute_import, unicode_literals

import io
import json
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

import requests

import responses

import testtools

import resources.lib.classes as classes
import resources.lib.comm as comm
import resources.lib.config as config


class CommTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/BC_EDGE.json'), 'rb') as f:
            self.BC_EDGE_JSON = io.BytesIO(f.read()).read()
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

    def test_get_airtime(self):
        ts = '2020-03-19T08:25:00.000+0000'
        expected = 'Thursday 19 Mar @ 7:25 PM'
        self.assertEqual(expected, comm.get_airtime(ts))

    @responses.activate
    def test_fetch_url(self):
        responses.add(responses.GET, 'http://foo.bar/',
                      body=u'\ufeffHello World', status=200)
        observed = comm.fetch_url('http://foo.bar/').decode('utf-8')
        self.assertEqual(observed, 'Hello World')

    @responses.activate
    def test_update_token(self):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        s = requests.Session()
        comm.update_token(s)
        observed = s.headers.get('x-media-mis-token')
        self.assertEqual('abcdef', observed)

    @responses.activate
    def test_get_bc_url(self):
        url = config.BC_EDGE_URL.format(account_id='foo', video_id='bar')
        responses.add(responses.GET, url, body=self.BC_EDGE_JSON, status=200)
        v = classes.Video()
        v.account_id = 'foo'
        v.video_id = 'bar'
        observed = comm.get_bc_url(v)
        expected = 'https://foo.bar/index.m3u8'
        self.assertEqual(expected, observed)

    @responses.activate
    def test_parse_json_video(self):
        responses.add(responses.GET, config.VIDEO_LIST_URL,
                      body=self.VIDEOS_JSON, status=200)
        video_list = []
        data = json.loads(comm.fetch_url(config.VIDEO_LIST_URL))
        for category in data['categories']:
            video_assets = category['videos']
            for video_asset in video_assets:
                video = comm.parse_json_video(video_asset)
                if video:
                    video_list.append(video)
        self.assertEqual(50, len(video_list))
        self.assertEqual('GF: Tigers v Giants Q4', video_list[0].title)

    @responses.activate
    def test_parse_json_live(self):
        responses.add(responses.GET, config.LIVE_LIST_URL,
                      body=self.LIVEMEDIA_JSON, status=200)
        listing = []
        data = json.loads(comm.fetch_url(config.LIVE_LIST_URL))
        for video in data:
            listing .append(video)
        self.assertEqual('AFL.TV', listing[0].get('title'))

    @responses.activate
    def test_get_videos(self):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.GET, config.VIDEO_LIST_URL,
                      body=self.VIDEOS_JSON, status=200)
        observed = comm.get_videos(config.VIDEO_LIST_URL)
        self.assertEqual(50, len(observed))
        self.assertEqual('GF: Tigers v Giants Q4', observed[0].title)

    @responses.activate
    def test_get_seasons(self):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.GET, config.SEASONS_URL,
                      body=self.SEASONS_JSON, status=200)
        observed = comm.get_seasons()
        self.assertEqual('CD_S2012014', observed[0].get('id'))

    @responses.activate
    def test_get_upcoming(self):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.GET, config.SEASONS_URL,
                      body=self.SEASONS_JSON, status=200)
        responses.add(responses.GET,
                      config.FIXTURE_URL.format('CD_S2020014',
                                                'CD_R202001401'),
                      body=self.RESULTS2020_JSON, status=200)
        observed = comm.get_upcoming()
        self.assertEqual(9, len(observed))

    @responses.activate
    def test_get_aflw_upcoming(self):
        responses.add(responses.GET, config.AFLW_SCORE_URL,
                      body=self.AFLW_SCORE_XML, status=200)
        observed = comm.get_aflw_upcoming()
        self.assertEqual(7, len(observed))

    @responses.activate
    def test_get_aflw_score(self):
        responses.add(responses.GET, config.AFLW_SCORE_URL,
                      body=self.AFLW_SCORE_XML, status=200)
        observed = comm.get_aflw_score('CD_M20202640101')
        self.assertEqual('[COLOR yellow] - [/COLOR]', observed)

    @responses.activate
    def test_get_aflw_videos(self):
        responses.add(responses.GET, config.AFLW_LONG_URL,
                      body=self.AFLW_LONG_XML, status=200)
        observed = comm.get_aflw_videos()
        self.assertEqual(25, len(observed))
        for v in observed:
            self.assertIsNotNone(v.video_id)

    @responses.activate
    def test_find_aflw_live_matches(self):
        responses.add(responses.GET, config.AFLW_INDEX_URL,
                      body=self.AFLW_INDEX_XML, status=200)
        for box in [
            'CD_M20202640101',
            'CD_M20202640102',
            'CD_M20202640103',
            'CD_M20202640104',
            'CD_M20202640105',
            'CD_M20202640106',
            'CD_M20202640107'
        ]:
            if box == 'CD_M20202640101':
                responses.add(responses.GET, config.AFLW_BOX_URL.format(box),
                              body=self.AFLW_BOX_LIVE_XML, status=200)
            else:
                responses.add(responses.GET, config.AFLW_BOX_URL.format(box),
                              body=self.AFLW_BOX_XML, status=200)

        observed = comm.find_aflw_live_matches()
        self.assertEqual(1, len(observed))

    @mock.patch('resources.lib.comm.get_upcoming', list)
    @mock.patch('resources.lib.comm.get_aflw_upcoming', list)
    @responses.activate
    def test_get_live_videos(self):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.GET, config.LIVE_LIST_URL,
                      body=self.LIVEMEDIA_JSON, status=200)
        observed = comm.get_live_videos()
        self.assertEqual(1, len(observed))
