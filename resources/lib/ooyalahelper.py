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

import urllib
import urllib2
import cookielib
import ssl

import json
import base64
import comm
import config
import xbmcaddon

import utils
import telstra_auth

from exception import AFLVideoException


cj = cookielib.CookieJar()
handler = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(handler)
addon = xbmcaddon.Addon()


# Fix for python > 2.7.8 ssl verification errors
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


def fetch_afl_json(url, data):
    """ send http POST and return the json response data"""
    data = urllib.urlencode(data)
    req = urllib2.Request(url, data, config.HEADERS)
    res = urllib2.urlopen(req)
    utils.log("Fetching URL: {0}".format(url))
    return res.read()


def get_afl_user_token():
    if addon.getSetting('LIVE_SUBSCRIPTION') == 'true':
        api_token = comm.fetch_token()
        opener.addheaders = [('x-media-mis-token', api_token)]
        username = addon.getSetting('LIVE_USERNAME')
        password = addon.getSetting('LIVE_PASSWORD')
        if int(addon.getSetting('SUBSCRIPTION_TYPE')):
            return telstra_auth.get_token(username, password)
        
        login_data = {'userIdentifier': addon.getSetting('LIVE_USERNAME'),
                'authToken': addon.getSetting('LIVE_PASSWORD'),
                'userIdentifierType': 'EMAIL',}
        login_json = fetch_afl_json(config.LOGIN_URL, login_data)
        data = json.loads(login_json)
        session_id = data['data'].get('artifactValue')
        
        try:
            session_url = config.SESSION_URL.format(urllib.quote(session_id))
            res = opener.open(session_url)
            data = json.loads(res.read())
            try:
                return data['subscriptions'][0].get('uuid')
            
            except IndexError as e:
                raise AFLVideoException('AFL Live Pass subscription expired')
             
        except urllib2.HTTPError as e:
            # Attempt to parse response even with a HTTP 400
            try:
                data = json.loads(e.read())
                if 'techMessage' in data:
                    raise AFLVideoException('Failed to fetch live streaming '
                                            'token: %s' 
                                            % data.get('techMessage'))
                if 'userMessage' in data:
                    raise AFLVideoException('Failed to fetch live streaming '
                                            'token: %s' 
                                            % data.get('userMessage'))
            except Exception as e:
                raise e
    
        raise Exception('Failed to fetch AFL Live streaming token')
    else:
        raise AFLVideoException('AFL Live Pass subscription is required.')


def get_afl_embed_token(user_token, video_id):
    """send our user token to get our embed token, including api key"""
    try:
        res = opener.open(config.EMBED_TOKEN_URL.format(user_token, video_id))
    except urllib2.HTTPError as e:
        try:
            data = json.loads(e.read())
            utils.log(data)
            raise Exception
        except Exception as e:
            raise e
    data = json.loads(res.read())
    return urllib.quote(data.get('token'))


def get_secure_token(secure_url, video_id):
    """send our embed token back with a few other url encoded parameters"""
    res = opener.open(secure_url, None)
    data = res.read()
    parsed_json = json.loads(data)
    ios_token = parsed_json['authorization_data'][video_id]['streams'][0]['url']['data']  # noqa
    return base64.b64decode(ios_token)


def get_m3u8_streams(secure_token_url):
    """ fetch our m3u8 file which contains streams of various qualities"""
    res = opener.open(secure_token_url, None)
    data = res.readlines()
    return data


def parse_m3u8_streams(data, live, secure_token_url):
    """ Parse the retrieved m3u8 stream list into a list of dictionaries
        then return the url for the highest quality stream. Different
        handling is required of live m3u8 files as they seem to only contain
        the destination filename and not the domain/path."""
    if live == 'true':
        qual = xbmcaddon.Addon().getSetting('LIVE_QUALITY')
    else:
        qual = xbmcaddon.Addon().getSetting('HLSQUALITY')
    if '#EXT-X-VERSION:3\n' in data:
        data.remove('#EXT-X-VERSION:3\n')
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

        if live == 'false':
            linelist.append(['URL', data[count + 1]])
        else:
            linelist.append(['URL', prepend_live + data[count + 1]])

        m3u_list.append(dict((i[0], i[1]) for i in linelist))
        count += 2
    sorted_m3u_list = sorted(m3u_list, key=lambda k: int(k['BANDWIDTH']))
    stream = sorted_m3u_list[int(qual)]['URL'][:-1]
    return stream


def get_m3u8_playlist(video_id, live, login_token, mode):
    """ Main function to call other functions that will return us our m3u8 HLS
        playlist as a string, which we can then write to a file for Kodi
        to use"""

    embed_token = get_afl_embed_token(login_token, video_id)

    authorize_url = config.AUTH_URL.format(config.PCODE, video_id, embed_token)
    secure_token_url = get_secure_token(authorize_url, video_id)

    if 'chunklist.m3u8' in secure_token_url:
        return secure_token_url

    m3u8_data = get_m3u8_streams(secure_token_url)
    m3u8_playlist_url = parse_m3u8_streams(m3u8_data, live, secure_token_url)
    return m3u8_playlist_url
