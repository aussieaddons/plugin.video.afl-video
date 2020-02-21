from __future__ import absolute_import, unicode_literals

import io
import json
import os
try:
    import mock
except ImportError:
    import unittest.mock as mock

from future.moves.urllib.parse import quote, quote_plus

import responses

import testtools

import resources.lib.config as config
import resources.lib.stream_auth as stream_auth
from resources.tests.fakes import fakes


class StreamAuthTests(testtools.TestCase):
    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/AUTH.json'),
                  'rb') as f:
            self.AUTH_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/AUTH_FAILED.json'),
                  'rb') as f:
            self.AUTH_FAILED_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/BP_AUTH.json'),
                  'rb') as f:
            self.BP_AUTH_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/BP_AUTH_FAIL.json'),
                  'rb') as f:
            self.BP_AUTH_FAIL_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/EMBED_TOKEN.json'),
                  'rb') as f:
            self.EMBED_TOKEN_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/EMBED_TOKEN_FAIL.json'),
                  'rb') as f:
            self.EMBED_TOKEN_FAIL_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/SESSION.json'),
                  'rb') as f:
            self.SESSION_JSON = io.BytesIO(f.read()).read()

    @mock.patch('resources.lib.stream_auth.cache.delete')
    def test_clear_ticket(self, mock_delete):
        stream_auth.clear_token()
        mock_delete.assert_called_with('AFLTOKEN')

    @mock.patch('resources.lib.stream_auth.addon.getSetting')
    @mock.patch('resources.lib.stream_auth.cache.get')
    def test_get_user_ticket_cached(self, mock_ticket, mock_sub_type):
        mock_ticket.return_value = 'foobar123456'
        mock_sub_type.return_value = '0'
        observed = stream_auth.get_user_token()
        self.assertEqual('foobar123456', observed)

    @mock.patch(
        'resources.lib.stream_auth.telstra_auth.TelstraAuth.get_free_token')
    @mock.patch('resources.lib.stream_auth.addon.getSetting')
    @mock.patch('resources.lib.stream_auth.cache.get')
    def test_get_user_ticket_free(self, mock_ticket, mock_sub_type,
                                  mock_token):
        mock_ticket.return_value = ''
        mock_sub_type.return_value = '1'
        mock_token.return_value = 'foobar456789'

    @mock.patch(
        'resources.lib.stream_auth.telstra_auth.TelstraAuth.get_mobile_token')
    @mock.patch('resources.lib.stream_auth.addon.getSetting')
    @mock.patch('resources.lib.stream_auth.cache.get')
    @responses.activate
    def test_get_user_ticket_mobile(self, mock_ticket, mock_setting,
                                    mock_token):
        def get_setting(param):
            if param == 'LIVE_SUBSCRIPTION':
                return 'true'
            else:
                return 3

        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        mock_ticket.return_value = ''
        mock_setting.side_effect = get_setting
        mock_token.return_value = 'foobar654321'
        observed = stream_auth.get_user_token()
        self.assertEqual('foobar654321', observed)

    @mock.patch('resources.lib.stream_auth.addon',
                fakes.FakeAddon(sub_type=0))
    @mock.patch('resources.lib.stream_auth.cache.get')
    @responses.activate
    def test_get_user_ticket_paid(self, mock_ticket):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.POST, config.LOGIN_URL,
                      body=self.BP_AUTH_JSON, status=200)
        responses.add(responses.GET,
                      config.SESSION_URL.format('artifactstring%23'),
                      body=self.SESSION_JSON, status=200)
        mock_ticket.return_value = ''
        observed = stream_auth.get_user_token()
        self.assertEqual(fakes.MIS_UUID, observed)

    @mock.patch('resources.lib.stream_auth.addon',
                fakes.FakeAddon(sub_type=0))
    @mock.patch('resources.lib.stream_auth.cache.get')
    @responses.activate
    def test_get_user_ticket_paid_fail(self, mock_ticket):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.POST, config.LOGIN_URL,
                      body=self.BP_AUTH_FAIL_JSON, status=200)
        mock_ticket.return_value = ''
        self.assertRaises(stream_auth.AussieAddonsException,
                          stream_auth.get_user_token)

    @mock.patch('resources.lib.stream_auth.addon',
                fakes.FakeAddon(sub_type=0, live_sub=False))
    def test_get_user_ticket_nosub(self):
        with testtools.ExpectedException(stream_auth.AussieAddonsException,
                                         'AFL Live Pass sub*'):
            stream_auth.get_user_token()

    @mock.patch('resources.lib.stream_auth.addon',
                fakes.FakeAddon(sub_type=2))
    def test_get_user_ticket_iap(self):
        observed = stream_auth.get_user_token()
        self.assertEqual(fakes.MIS_UUID, observed)

    @mock.patch('resources.lib.stream_auth.addon',
                fakes.FakeAddon(sub_type=2, iap_token='gghhiijjkkllmm'))
    def test_get_user_ticket_iap_fail_bad_format(self):
        with testtools.ExpectedException(stream_auth.AussieAddonsException,
                                         'mis-uuid token must*'):
            stream_auth.get_user_token()

    @responses.activate
    def test_get_embed_token(self):
        responses.add(responses.GET,
                      config.EMBED_TOKEN_URL.format(fakes.MIS_UUID, 'foo'),
                      body=self.EMBED_TOKEN_JSON, status=200)
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        observed = stream_auth.get_embed_token(fakes.MIS_UUID, 'foo')
        self.assertEqual(quote('http://foobar.com/video'), observed)

    @responses.activate
    @mock.patch('resources.lib.stream_auth.addon',
                fakes.FakeAddon(sub_type=1))
    @mock.patch('resources.lib.stream_auth.cache.delete')
    def test_get_embed_token_fail(self, mock_delete):
        responses.add(responses.GET,
                      config.EMBED_TOKEN_URL.format(fakes.MIS_UUID, 'foo'),
                      body=self.EMBED_TOKEN_FAIL_JSON, status=400)
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        with testtools.ExpectedException(stream_auth.AussieAddonsException,
                                         'Stored login token*'):
            stream_auth.get_embed_token(fakes.MIS_UUID, 'foo')
        mock_delete.assert_called_with('AFLTOKEN')

    @responses.activate
    def test_get_secure_token(self):
        responses.add(responses.GET, 'https://foo.bar/', body=self.AUTH_JSON,
                      status=200)
        observed = stream_auth.get_secure_token('https://foo.bar/',
                                                 fakes.VIDEO_ID)
        self.assertEqual(fakes.M3U8_URL_OOYALA, observed)

    @responses.activate
    def test_get_secure_token_fail_keyerror(self):
        responses.add(responses.GET, 'https://foo.bar/',
                      body=self.AUTH_FAILED_JSON,
                      status=200)
        self.assertRaises(stream_auth.AussieAddonsException,
                          stream_auth.get_secure_token,
                          'https://foo.bar/',
                          fakes.VIDEO_ID)

    @responses.activate
    @mock.patch('resources.lib.stream_auth.cache.get')
    def test_get_m3u8_playlist(self, mock_ticket):
        mock_ticket.return_value = 'foobar123456'
        auth_url = config.AUTH_URL.format(
            config.PCODE, fakes.VIDEO_ID,
            quote_plus('http://foobar.com/video'))
        responses.add(responses.GET, auth_url,
                      body=self.AUTH_JSON, status=200)
        responses.add(responses.GET,
                      config.EMBED_TOKEN_URL.format(fakes.MIS_UUID,
                                                    fakes.VIDEO_ID),
                      body=self.EMBED_TOKEN_JSON, status=200)
        observed = stream_auth.get_m3u8_playlist(fakes.VIDEO_ID, '')
        self.assertEqual(fakes.M3U8_URL_OOYALA, observed)
