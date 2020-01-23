from __future__ import absolute_import, unicode_literals

import io
import json
import os
import re
try:
    import mock
except ImportError:
    import unittest.mock as mock

import responses

import testtools

import resources.lib.config as config
import resources.lib.telstra_auth as telstra_auth
from resources.tests.fakes import fakes


class TelstraAuthTests(testtools.TestCase):
    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/AFL_TOKEN.json'), 'rb') as f:
            self.AFL_TOKEN_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/MIS_UUID.json'), 'rb') as f:
            self.MIS_UUID_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/MYID_TOKEN_RESP.json'),
                  'rb') as f:
            self.MYID_TOKEN_RESP_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/OFFERS_RESP.json'),
                  'rb') as f:
            self.OFFERS_RESP_JSON = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/json/OFFERS_FAIL_RESP.json'),
                'rb') as f:
            self.OFFERS_FAIL_RESP_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/ORDER_RESP.json'),
                  'rb') as f:
            self.ORDER_RESP_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/STATUS_RESP.json'),
                  'rb') as f:
            self.STATUS_RESP_JSON = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/json/STATUS_FAIL_RESP.json'),
                'rb') as f:
            self.STATUS_FAIL_RESP_JSON = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/html/SPC_RESP.html'),
                'rb') as f:
            self.SPC_RESP_HTML = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/html/MYID_AUTH_RESP.html'),
                'rb') as f:
            self.MYID_AUTH_RESP_HTML = io.BytesIO(f.read()).read()
        with open(
                os.path.join(cwd, 'fakes/html/MYID_RESUME_AUTH_RESP.html'),
                'rb') as f:
            self.MYID_RESUME_AUTH_RESP_HTML = io.BytesIO(f.read()).read()

    @responses.activate
    @mock.patch('os.urandom')
    @mock.patch('uuid.uuid4')
    def test_get_free_token(self, mock_uuid, mock_random):
        mock_uuid.side_effect = fakes.FAKE_UUID
        mock_random.side_effect = fakes.FAKE_RANDOM
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.POST, config.AFL_LOGIN_URL,
                      body=self.MIS_UUID_JSON, status=200)
        escaped_spc_url = re.escape(
            config.SPORTSPASS_URL).replace('\\{', '{').replace('\\}', '}')
        spc_url = re.compile(escaped_spc_url.format('.*'))
        responses.add(responses.GET, spc_url,
                      body=self.SPC_RESP_HTML, status=200)
        responses.add(responses.GET, config.MYID_AUTHORIZATION_URL,
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        responses.add(responses.POST,
                      config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                      body=self.MYID_RESUME_AUTH_RESP_HTML,
                      status=200)
        for url in config.SSO_SESSION_HANDLER_URLS:
            responses.add(responses.POST, url,
                          json={'status': 'success'},
                          status=200)

        responses.add(responses.GET,
                      '{0}{1}'.format(
                          config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                          '?ctfr-proceed=true'),
                      headers={'Set-Cookie': fakes.FAKE_BPSESSION_COOKIE,
                               'Location':
                                   fakes.MYID_RESUME_AUTH_REDIRECT_URL},
                      status=302)
        responses.add(responses.GET, fakes.MYID_RESUME_AUTH_REDIRECT_URL,
                      status=200)
        responses.add(responses.POST, config.MYID_TOKEN_URL,
                      body=self.MYID_TOKEN_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      body=self.OFFERS_RESP_JSON,
                      status=200)
        responses.add(responses.POST, config.MEDIA_ORDER_URL,
                      body=self.ORDER_RESP_JSON,
                      status=201)
        auth = telstra_auth.TelstraAuth('foo', 'bar')
        observed = auth.get_free_token()
        self.assertEqual(fakes.MIS_UUID, observed)

    @responses.activate
    @mock.patch('os.urandom')
    @mock.patch('uuid.uuid4')
    def test_get_free_token_fail_userpass(self, mock_uuid, mock_random):
        mock_uuid.side_effect = fakes.FAKE_UUID
        mock_random.side_effect = fakes.FAKE_RANDOM
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.POST, config.AFL_LOGIN_URL,
                      body=self.MIS_UUID_JSON, status=200)
        escaped_spc_url = re.escape(
            config.SPORTSPASS_URL).replace('\\{', '{').replace('\\}', '}')
        spc_url = re.compile(escaped_spc_url.format('.*'))
        responses.add(responses.GET, spc_url,
                      body=self.SPC_RESP_HTML, status=200)
        responses.add(responses.GET, config.MYID_AUTHORIZATION_URL,
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        responses.add(responses.POST,
                      config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        auth = telstra_auth.TelstraAuth('foo', 'wrongpassword')
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_free_token)

    @responses.activate
    @mock.patch('os.urandom')
    @mock.patch('uuid.uuid4')
    def test_get_free_token_fail_no_offer(self, mock_uuid, mock_random):
        mock_uuid.side_effect = fakes.FAKE_UUID
        mock_random.side_effect = fakes.FAKE_RANDOM
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.POST, config.AFL_LOGIN_URL,
                      body=self.MIS_UUID_JSON, status=200)
        escaped_spc_url = re.escape(
            config.SPORTSPASS_URL).replace('\\{', '{').replace('\\}', '}')
        spc_url = re.compile(escaped_spc_url.format('.*'))
        responses.add(responses.GET, spc_url,
                      body=self.SPC_RESP_HTML, status=200)
        responses.add(responses.GET, config.MYID_AUTHORIZATION_URL,
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        responses.add(responses.POST,
                      config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                      body=self.MYID_RESUME_AUTH_RESP_HTML,
                      status=200)
        for url in config.SSO_SESSION_HANDLER_URLS:
            responses.add(responses.POST, url,
                          json={'status': 'success'},
                          status=200)

        responses.add(responses.GET,
                      '{0}{1}'.format(
                          config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                          '?ctfr-proceed=true'),
                      headers={'Set-Cookie': fakes.FAKE_BPSESSION_COOKIE,
                               'Location':
                                   fakes.MYID_RESUME_AUTH_REDIRECT_URL},
                      status=302)
        responses.add(responses.GET, fakes.MYID_RESUME_AUTH_REDIRECT_URL,
                      status=200)
        responses.add(responses.POST, config.MYID_TOKEN_URL,
                      body=self.MYID_TOKEN_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      body=self.OFFERS_FAIL_RESP_JSON,
                      status=200)
        auth = telstra_auth.TelstraAuth('foo', 'bar')
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_free_token)

    @responses.activate
    @mock.patch('os.urandom')
    @mock.patch('uuid.uuid4')
    def test_get_free_token_fail_no_eligible(self, mock_uuid, mock_random):
        mock_uuid.side_effect = fakes.FAKE_UUID
        mock_random.side_effect = fakes.FAKE_RANDOM
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.POST, config.AFL_LOGIN_URL,
                      body=self.MIS_UUID_JSON, status=200)
        escaped_spc_url = re.escape(
            config.SPORTSPASS_URL).replace('\\{', '{').replace('\\}', '}')
        spc_url = re.compile(escaped_spc_url.format('.*'))
        responses.add(responses.GET, spc_url,
                      body=self.SPC_RESP_HTML, status=200)
        responses.add(responses.GET, config.MYID_AUTHORIZATION_URL,
                      body=self.MYID_AUTH_RESP_HTML,
                      status=200)
        responses.add(responses.POST,
                      config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                      body=self.MYID_RESUME_AUTH_RESP_HTML,
                      status=200)
        for url in config.SSO_SESSION_HANDLER_URLS:
            responses.add(responses.POST, url,
                          json={'status': 'success'},
                          status=200)

        responses.add(responses.GET,
                      '{0}{1}'.format(
                          config.MYID_RESUME_AUTHORIZATION_URL.format('ABCDE'),
                          '?ctfr-proceed=true'),
                      headers={'Set-Cookie': fakes.FAKE_BPSESSION_COOKIE,
                               'Location':
                                   fakes.MYID_RESUME_AUTH_REDIRECT_URL},
                      status=302)
        responses.add(responses.GET, fakes.MYID_RESUME_AUTH_REDIRECT_URL,
                      status=200)
        responses.add(responses.POST, config.MYID_TOKEN_URL,
                      body=self.MYID_TOKEN_RESP_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      json={'userMessage': 'No eligible services'},
                      status=404)
        auth = telstra_auth.TelstraAuth('foo', 'bar')
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_free_token)

    @responses.activate
    def test_get_mobile_token(self):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.POST, config.AFL_LOGIN_URL,
                      body=self.MIS_UUID_JSON, status=200)
        responses.add(responses.GET, config.MOBILE_ID_URL,
                      headers={'Set-Cookie': fakes.FAKE_MOBILE_COOKIE},
                      status=200)
        responses.add(responses.POST, config.MOBILE_OAUTH_URL,
                      body=self.AFL_TOKEN_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      body=self.OFFERS_RESP_JSON,
                      status=200)
        responses.add(responses.POST, config.MEDIA_ORDER_URL,
                      body=self.ORDER_RESP_JSON,
                      status=201)
        auth = telstra_auth.TelstraAuth()
        observed = auth.get_mobile_token()
        self.assertEqual(fakes.MIS_UUID, observed)

    @responses.activate
    def test_get_mobile_token_fail_no_mobile_data(self):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.POST, config.AFL_LOGIN_URL,
                      body=self.MIS_UUID_JSON, status=200)
        responses.add(responses.GET, config.MOBILE_ID_URL,
                      headers={'Set-Cookie': fakes.FAKE_MOBILE_COOKIE_NO_DATA},
                      status=204)
        auth = telstra_auth.TelstraAuth()
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_mobile_token)

    @responses.activate
    def test_get_mobile_token_fail_no_offer(self):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.POST, config.AFL_LOGIN_URL,
                      body=self.MIS_UUID_JSON, status=200)
        responses.add(responses.GET, config.MOBILE_ID_URL,
                      headers={'Set-Cookie': fakes.FAKE_MOBILE_COOKIE},
                      status=200)
        responses.add(responses.POST, config.MOBILE_OAUTH_URL,
                      body=self.AFL_TOKEN_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      body=self.OFFERS_FAIL_RESP_JSON,
                      status=200)
        auth = telstra_auth.TelstraAuth()
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_mobile_token)

    @responses.activate
    def test_get_mobile_token_fail_no_eligible(self):
        responses.add(responses.POST, config.TOKEN_URL,
                      body=json.dumps({'token': 'abcdef'}), status=200)
        responses.add(responses.POST, config.AFL_LOGIN_URL,
                      body=self.MIS_UUID_JSON, status=200)
        responses.add(responses.GET, config.MOBILE_ID_URL,
                      headers={'Set-Cookie': fakes.FAKE_MOBILE_COOKIE},
                      status=200)
        responses.add(responses.POST, config.MOBILE_OAUTH_URL,
                      body=self.AFL_TOKEN_JSON,
                      status=200)
        responses.add(responses.GET, config.OFFERS_URL,
                      json={'userMessage': 'No eligible services'},
                      status=404)
        auth = telstra_auth.TelstraAuth()
        self.assertRaises(telstra_auth.TelstraAuthException,
                          auth.get_mobile_token)
