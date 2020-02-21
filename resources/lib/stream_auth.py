import json

from future.moves.urllib.parse import quote, urlencode

import requests

from aussieaddonscommon import session
from aussieaddonscommon import utils
from aussieaddonscommon.exceptions import AussieAddonsException

from resources.lib import comm
from resources.lib import config
from resources.lib import telstra_auth

import xbmcaddon

import xbmcgui

try:
    import StorageServer
except ImportError:
    import resources.lib.storageserverdummy as StorageServer

cache = StorageServer.StorageServer(utils.get_addon_id(), 1)
addon = xbmcaddon.Addon()

sess = session.Session()


def clear_token():
    """Remove stored token from cache storage"""
    try:
        cache.delete('AFLTOKEN')
        utils.dialog_message('Login token removed')
    except AttributeError:
        pass


def fetch_session_id(url, data):
    """send http POST and return the json response data"""
    data = urlencode(data)
    sess.headers = config.HEADERS
    comm.update_token(sess)
    res = sess.post(url, data)
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        utils.log(e.response.text)
        raise Exception(e)
    return res.text


def get_sub_type():
    return int(addon.getSetting('SUBSCRIPTION_TYPE'))


def get_user_token():
    """Send user login info and retrieve token for session"""
    # in-app purchase/manual
    subscription_type = get_sub_type()
    if subscription_type == 2:
        iap_token = addon.getSetting('IAP_TOKEN').lower()
        try:
            int(iap_token, 16)
        except ValueError:
            raise AussieAddonsException(
                'mis-uuid token must be 32 characters in length, and only '
                'contain numbers 0-9 and letters a-f')
        if len(iap_token) != 32:
            raise AussieAddonsException(
                'mis-uuid token must be 32 characters in length, and only '
                'contain numbers 0-9 and letters a-f')
        token = 'mis-uuid-{0}'.format(iap_token)
        utils.log('Using manual token: {0}******'.format(token[:-6]))
        return token

    stored_token = cache.get('AFLTOKEN')
    if stored_token:
        utils.log('Using token: {0}******'.format(stored_token[:-6]))
        return stored_token

    if addon.getSetting('LIVE_SUBSCRIPTION') == 'true':
        username = addon.getSetting('LIVE_USERNAME')
        password = addon.getSetting('LIVE_PASSWORD')

        if subscription_type == 1:  # free subscription
            auth = telstra_auth.TelstraAuth(username, password)
            token = auth.get_free_token()
        elif subscription_type == 3:  # mobile activated subscription
            auth = telstra_auth.TelstraAuth()
            token = auth.get_mobile_token()
        else:  # paid afl.com.au
            login_data = {'userIdentifier': addon.getSetting('LIVE_USERNAME'),
                          'authToken': addon.getSetting('LIVE_PASSWORD'),
                          'userIdentifierType': 'EMAIL'}
            login_json = fetch_session_id(config.LOGIN_URL, login_data)
            data = json.loads(login_json)
            if data.get('responseCode') != 0:
                raise AussieAddonsException('Invalid Telstra ID login/'
                                            'password for paid afl.com.au '
                                            '/ linked subscription.')
            session_id = data['data'].get('artifactValue')

            try:
                sess.headers.update({'Authorization': None})
                encoded_session_id = quote(session_id)
                session_url = config.SESSION_URL.format(encoded_session_id)
                res = sess.get(session_url)
                data = json.loads(res.text)
                token = data.get('uuid')

            except requests.exceptions.HTTPError as e:
                utils.log(e.response.text)
                raise e
        cache.set('AFLTOKEN', token)
        utils.log('Using token: {0}******'.format(token[:-6]))
        return token
    else:
        raise AussieAddonsException('AFL Live Pass subscription is required '
                                    'for this content. Please open the '
                                    'add-on settings to enable and configure.')


def iap_help():
    xbmcgui.Dialog().textviewer(
        'Instructions for finding mis-uuid',
        'Open the AFL app on your device and obtain your LIVE PASS '
        'subscription. Once logged in the purple T at the top right of the '
        'home screen should turn green. Press on the green T which will open '
        'the settings, and go into "AFL Live Pass Subscription". Scroll to '
        'the bottom of the screen to find the mis-uuid token. Enter the 32 '
        'digit hexadecimal number that comes after "mis-uuid-" into the '
        'subscription token setting.')


def get_media_auth_token(pai, video_id):
    """
    send our user token to get our embed token, including api key
    """
    url = config.MEDIA_AUTH_URL.format(code=video_id, pai=pai)

    try:
        data = comm.fetch_url(url, request_token=True)
        json_data = json.loads(data)
        if json_data.get('Fault'):
            raise AussieAddonsException(
                json_data.get('fault').get('faultstring'))
        media_auth_token = json_data.get('urlSigningToken')
    except requests.exceptions.HTTPError as e:
        utils.log('Error getting embed token. '
                  'Response: {0}'.format(e.response.text))
        cache.delete('AFLTOKEN')
        if e.response.status_code == 401:
            raise AussieAddonsException('Login token has expired, '
                                        'please try again.')
        else:
            raise e
    return media_auth_token
