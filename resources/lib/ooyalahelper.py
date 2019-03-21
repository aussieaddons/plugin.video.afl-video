# Ooyalahelper module copyright 2016 Glenn Guy
#
# Ooyalahelper module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ooyalahelper module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ooyalahelper module. If not, see <http://www.gnu.org/licenses/>.


# This module contains functions for interacting with the Ooyala API


import base64
import comm
import config
import json
import re
import requests
import urllib
import xbmcaddon
import xbmcgui

import telstra_auth

from aussieaddonscommon.exceptions import AussieAddonsException
from aussieaddonscommon import session
from aussieaddonscommon import utils

try:
    import StorageServer
except ImportError:
    import storageserverdummy as StorageServer


cache = StorageServer.StorageServer(utils.get_addon_id(), 1)
addon = xbmcaddon.Addon()
subscription_type = int(addon.getSetting('SUBSCRIPTION_TYPE'))
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
    data = urllib.urlencode(data)
    sess.headers = config.HEADERS
    comm.update_token(sess)
    res = sess.post(url, data)
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        utils.log(e.response.text)
        raise Exception(e)
    return res.text


def get_user_token():
    """Send user login info and retrieve token for session"""
    # in-app purchase/manual
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
            token = telstra_auth.get_token(username, password)
        elif subscription_type == 3:  # mobile activated subscription
            token = telstra_auth.get_mobile_token()
        else:  # paid afl.com.au
            login_data = {'userIdentifier': addon.getSetting('LIVE_USERNAME'),
                          'authToken': addon.getSetting('LIVE_PASSWORD'),
                          'userIdentifierType': 'EMAIL'}
            login_json = fetch_session_id(config.LOGIN_URL, login_data)
            data = json.loads(login_json)
            utils.log(data)
            if data.get('responseCode') != 0:
                raise AussieAddonsException('Invalid Telstra ID login/'
                                            'password for paid afl.com.au '
                                            '/ linked subscription.')
            session_id = data['data'].get('artifactValue')

            try:
                sess.headers.update({'Authorization': None})
                encoded_session_id = urllib.quote(session_id)
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


def get_embed_token(user_token, video_id):
    """send our user token to get our embed token, including api key"""
    try:
        comm.update_token(sess)
        embed_token_url = config.EMBED_TOKEN_URL.format(user_token, video_id)
        utils.log("Fetching embed token: {0}".format(embed_token_url))
        try:
            res = sess.get(embed_token_url)
        except requests.exceptions.SSLError:
            cache.delete('AFLTOKEN')
            raise AussieAddonsException(
                'Your version of Kodi is too old to support live streaming. '
                'Please upgrade to the latest version.')
    except requests.exceptions.HTTPError as e:
        if subscription_type == 0:  # paid afl.com.au/linked
            cache.delete('AFLTOKEN')
            raise AussieAddonsException(
                'Paid or linked subscription not found for supplied username '
                'and password. Please check the subscription type in settings '
                'is correct or your subscription has been linked to your '
                'Telstra ID in the Android/iOS app')
        elif subscription_type in [1, 3]:  # free/mobile sub
            cache.delete('AFLTOKEN')
            utils.log(e.response.text)
            if e.response.status_code == 400:
                raise AussieAddonsException(
                    'Stored login token has expired, please try to play this '
                    'item again. If this error persists please submit an '
                    'issue on our github (github.com/aussieaddons/plugin.'
                    'video.afl-video')
            else:
                raise e
        else:  # in-app purchase/manual
            raise AussieAddonsException(
                'mis-uuid token is invalid, please check the token in '
                'the settings is correct and try again')

    data = json.loads(res.text)
    return urllib.quote(data.get('token'))


def get_secure_token(secure_url, video_id):
    """send our embed token back with a few other url encoded parameters"""
    res = sess.get(secure_url)
    try:
        parsed_json = json.loads(res.text)
    except ValueError:
        utils.log('Failed to load JSON. Data is: {0}'.format(res.text))
        if '<html' in res.text:  # smart DNS redirects
            raise AussieAddonsException(
                'Failed to get authorization token. Please ensure any smart '
                'DNS service is disabled.')
        else:
            raise Exception('Failed to get authorization token.')
    if parsed_json.get('authorized') is False:
        raise AussieAddonsException(
            'Failed to get authorization token: {0}'
            ''.format(parsed_json.get('message')))

    auth_data = parsed_json.get('authorization_data')

    utils.log('auth_data: %s' % auth_data)
    video = auth_data.get(video_id)

    if video.get('authorized') is False:
        raise AussieAddonsException(
            'Failed to obtain secure token: {0}.\n'
            'Check your subscription is valid.'.format(video.get('message')))
    try:
        streams = video.get('streams')
        stream_url = base64.b64decode(streams[0]['url']['data'])
        widevine_url = streams[0].get('widevine_server_path')
        return {'stream_url': stream_url, 'widevine_url': widevine_url}
    except Exception as e:
        raise AussieAddonsException(
            'Failed to get stream URL: {0}'.format(e))


def get_m3u8_streams(secure_token_url):
    """fetch our m3u8 file which contains streams of various qualities"""
    res = sess.get(secure_token_url)
    data = res.text.splitlines()
    return data


def parse_m3u8_streams(data, live, secure_token_url):
    """Parse m3u8 stream

    Parse the retrieved m3u8 stream list into a list of dictionaries
    then return the url for the highest quality stream. Different
    handling is required of live m3u8 files as they seem to only contain
    the destination filename and not the domain/path.
    """

    if live:
        qual = int(xbmcaddon.Addon().getSetting('LIVE_QUALITY'))
        if qual == config.MAX_LIVE_QUAL:
            qual = -1
    else:
        qual = int(xbmcaddon.Addon().getSetting('REPLAYQUALITY'))
        if qual == config.MAX_REPLAY_QUAL:
            qual = -1

    m3u_list = []
    base_url = secure_token_url[:secure_token_url.rfind('/') + 1]
    base_domain = secure_token_url[:secure_token_url.find('/', 8) + 1]
    m3u8_lines = iter(data)
    for line in m3u8_lines:
            stream_inf = '#EXT-X-STREAM-INF:'
            if line.startswith(stream_inf):
                line = line[len(stream_inf):]
            else:
                continue

            csv_list = re.split(',(?=(?:(?:[^"]*"){2})*[^"]*$)', line)
            linelist = [i.split('=') for i in csv_list]

            uri = next(m3u8_lines)

            if uri.startswith('/'):
                linelist.append(['URL', base_domain + uri])
            elif uri.find('://') == -1:
                linelist.append(['URL', base_url + uri])
            else:
                linelist.append(['URL', uri])
            m3u_list.append(dict((i[0], i[1]) for i in linelist))
    sorted_m3u_list = sorted(m3u_list, key=lambda k: int(k['BANDWIDTH']))
    try:
        stream = sorted_m3u_list[qual]['URL']
    except IndexError as e:
        utils.log('Quality setting: {0}'.format(qual))
        utils.log('Sorted m3u8 list: {0}'.format(sorted_m3u_list))
        raise e
    return stream


def get_m3u8_playlist(video_id, live, login_token=None):
    """Get m3u8 playlist

    Main function to call other functions that will return us our m3u8 HLS
    playlist as a string, which we can then write to a file for Kodi
    to use
    """

    auth_url = config.AUTH_URL.format(config.PCODE, video_id)

    if login_token:
        embed_token = get_embed_token(login_token, video_id)
        auth_url = auth_url + '&embedToken=' + embed_token

    stream_data = get_secure_token(auth_url, video_id)
    return stream_data


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
