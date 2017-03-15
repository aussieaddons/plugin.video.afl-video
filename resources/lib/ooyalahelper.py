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
import requests
import sys
import urllib
import xbmcaddon

import telstra_auth
import utils

from exception import AFLVideoException

try:
   import StorageServer
except:
    utils.log("script.common.plugin.cache not found!")
    import storageserverdummy as StorageServer
cache = StorageServer.StorageServer(config.ADDON_ID, 1)

# Ignore InsecureRequestWarning warnings
requests.packages.urllib3.disable_warnings()
session = requests.Session()
session.verify = False

addon = xbmcaddon.Addon()
free_subscription = int(addon.getSetting('SUBSCRIPTION_TYPE'))

def clear_token():
    """Remove stored token from cache storage"""
    cache.delete('AFLTOKEN')

def fetch_session_id(url, data):
    """ send http POST and return the json response data"""
    data = urllib.urlencode(data)
    session.headers = config.HEADERS
    comm.update_token(session)
    utils.log("Fetching URL: {0}".format(url))
    res = session.post(url, data)
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        utils.log(res.text)
        raise Exception(e)
    return res.text


def get_user_token():
    """ Send user login info and retrieve token for session"""
    stored_token = cache.get('AFLTOKEN')
    if stored_token != '':
        utils.log('Using token: {0}******'.format(stored_token[:-6]))
        return stored_token
    
    if addon.getSetting('LIVE_SUBSCRIPTION') == 'true':
        username = addon.getSetting('LIVE_USERNAME')
        password = addon.getSetting('LIVE_PASSWORD')

        if free_subscription:
            token = telstra_auth.get_token(username, password)
        else:
            login_data = {'userIdentifier': addon.getSetting('LIVE_USERNAME'),
                          'authToken': addon.getSetting('LIVE_PASSWORD'),
                          'userIdentifierType': 'EMAIL'}
            login_json = fetch_session_id(config.LOGIN_URL, login_data)
            data = json.loads(login_json)
            if data.get('responseCode') != 0:
                raise AFLVideoException('Invalid login/password for paid'
                                        ' afl.com.au subscription.')
            session_id = data['data'].get('artifactValue')
    
            try:
                session.headers.update({'Authorization': None})
                encoded_session_id = urllib.quote(session_id)
                session_url = config.SESSION_URL.format(encoded_session_id)
                res = session.get(session_url)
                res.raise_for_status()
                data = json.loads(res.text)
                token = data.get('uuid')
    
            except requests.exceptions.HTTPError as e:
                utils.log(res.text)
                raise e
        cache.set('AFLTOKEN', token)
        utils.log('Using token: {0}******'.format(token[:-6]))
        return token
    else:
        raise AFLVideoException('AFL Live Pass subscription is required.')


def get_embed_token(user_token, video_id):
    """send our user token to get our embed token, including api key"""
    try:
        comm.update_token(session)
        embed_token_url = config.EMBED_TOKEN_URL.format(user_token, video_id)
        utils.log("Fetching embed token: {0}".format(embed_token_url))
        try:
            res = session.get(embed_token_url)
        except requests.exceptions.SSLError:
            cache.delete('AFLTOKEN')
            raise AFLVideoException('Your version of Kodi is too old for live '
                                    'streaming. Please upgrade to the latest '
                                    'version of Kodi.')
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if not free_subscription:
            cache.delete('AFLTOKEN')
            raise AFLVideoException('Paid subscription not found for '
                                        'supplied username/password. Please '
                                        'check the subscription type in '
                                        'settings is correct.')
        else:
            utils.log(res.text)
            cache.delete('AFLTOKEN')
            raise e
    data = json.loads(res.text)
    return urllib.quote(data.get('token'))


def get_secure_token(secure_url, video_id):
    """send our embed token back with a few other url encoded parameters"""
    res = session.get(secure_url)
    try:
        parsed_json = json.loads(res.text)
    except ValueError:
        utils.log('Failed to load JSON. Data is: {0}'.format(res.text))
    ios_token = parsed_json['authorization_data'][video_id]['streams'][0]['url']['data']  # noqa
    return base64.b64decode(ios_token)


def get_m3u8_streams(secure_token_url):
    """ fetch our m3u8 file which contains streams of various qualities"""
    res = session.get(secure_token_url)
    data = res.text.splitlines()
    return data


def parse_m3u8_streams(data, live, secure_token_url):
    """ Parse the retrieved m3u8 stream list into a list of dictionaries
        then return the url for the highest quality stream. Different
        handling is required of live m3u8 files as they seem to only contain
        the destination filename and not the domain/path."""
    if live:
        qual = int(xbmcaddon.Addon().getSetting('LIVE_QUALITY'))
        if qual == config.MAX_LIVE_QUAL:
            qual = -1
    else:
        qual = int(xbmcaddon.Addon().getSetting('REPLAYQUALITY'))
        if qual == config.MAX_REPLAY_QUAL:
            qual = -1

    if '#EXT-X-VERSION:3' in data:
        data.remove('#EXT-X-VERSION:3')
    count = 1
    m3u_list = []
    prepend_live = secure_token_url[:secure_token_url.find('index-root')]
    while count < len(data):
        line = data[count]
        line = line.strip('#EXT-X-STREAM-INF:')
        line = line.strip('PROGRAM-ID=1,')
        line = line[:line.find('CODECS')]

        if line.endswith(','):
            line = line[:-1]

        line = line.strip()
        line = line.split(',')
        linelist = [i.split('=') for i in line]

        if not live:
            linelist.append(['URL', data[count + 1]])
        else:
            linelist.append(['URL', prepend_live + data[count + 1]])

        m3u_list.append(dict((i[0], i[1]) for i in linelist))
        count += 2
    sorted_m3u_list = sorted(m3u_list, key=lambda k: int(k['BANDWIDTH']))
    stream = sorted_m3u_list[qual]['URL']
    return stream


def get_m3u8_playlist(video_id, live, login_token):
    """ Main function to call other functions that will return us our m3u8 HLS
        playlist as a string, which we can then write to a file for Kodi
        to use"""

    embed_token = get_embed_token(login_token, video_id)

    authorize_url = config.AUTH_URL.format(config.PCODE, video_id, embed_token)
    secure_token_url = get_secure_token(authorize_url, video_id)

    if 'chunklist.m3u8' in secure_token_url:
        return secure_token_url

    m3u8_data = get_m3u8_streams(secure_token_url)
    m3u8_playlist_url = parse_m3u8_streams(m3u8_data, live, secure_token_url)
    return m3u8_playlist_url
