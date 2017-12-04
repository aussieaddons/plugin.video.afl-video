#
#     AFL Video Kodi Add-on
#     Copyright (C) 2016 Andy Botting
#
#     AFL Video is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     AFL Video is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this add-on. If not, see <http://www.gnu.org/licenses/>.
#

import classes
import config
import datetime
import json
import time
import xbmcaddon

from aussieaddonscommon import exceptions
from aussieaddonscommon import session
from aussieaddonscommon import utils

from bs4 import BeautifulStoneSoup

# Use local etree to get v1.3.0
import etree.ElementTree as ET

ADDON = xbmcaddon.Addon()


def get_team(team_id):
    """Return the team from a given team ID"""
    for t in config.TEAMS:
        if t['team_id'] == team_id:
            return t


def fetch_url(url, data=None, headers=None, request_token=False):
    """Simple function that fetches a URL using requests."""
    with session.Session() as sess:
        if headers:
            sess.headers.update(headers)

        # Token headers
        if request_token:
            update_token(sess)

        if data:
            request = sess.post(url, data)
        else:
            request = sess.get(url)
        try:
            request.raise_for_status()
        except Exception as e:
            # Just re-raise for now
            raise e
        data = request.text
    return data


def update_token(sess):
    """Update token

    This functions performs a HTTP POST to the token URL and it will update
    the requests session with a token required for API calls
    """
    res = sess.post(config.TOKEN_URL)
    try:
        token = json.loads(res.text).get('token')
    except Exception as e:
        raise exceptions.AussieAddonsException(
            'Failed to retrieve API token: {0}\n'
            'Service may be currently unavailable.'.format(e))
    sess.headers.update({'x-media-mis-token': token})


def get_attr(attrs, key):
    for attr in attrs:
        if attr.get('attrName') == key:
            return attr.get('attrValue')


def parse_json_video(video_data):
    """Parse JSON stream data

    Parse the JSON data and construct a video object from it for a list
    of videos
    """
    attrs = video_data.get('customAttributes')
    if not attrs:
        return

    video = classes.Video()
    video.title = utils.ensure_ascii(video_data.get('title'))
    video.description = utils.ensure_ascii(video_data.get('description'))
    video.thumbnail = video_data.get('thumbnailPath')
    try:
        timestamp = time.mktime(time.strptime(video_data['customPublishDate'],
                                              '%Y-%m-%dT%H:%M:%S.%f+0000'))
        video.date = datetime.date.fromtimestamp(timestamp)
    except Exception:
        pass

    if video_data.get('entitlement'):
        video.subscription_required = True

    # Look for 'national' stream (e.g. Foxtel)
    video_id = get_attr(attrs, 'ooyala embed code')

    if not video_id:
        # Look for configured state stream
        state = ADDON.getSetting('STATE')
        video_id = get_attr(attrs, 'state-' + state)

    if not video_id:
        # Fall back to the VIC stream
        video_id = get_attr(attrs, 'state-VIC')

    video.ooyalaid = video_id
    video.live = False
    return video


def parse_json_live(video_data):
    """Parse JSON live stream data

    Parse the JSON data for live match and construct a video object from it
    for a list of videos
    """
    video_stream = video_data.get('videoStream')
    if not video_stream:
        return

    attrs = video_stream.get('customAttributes')
    if not attrs:
        return

    video = classes.Video()
    title = utils.ensure_ascii(video_data.get('title'))
    video.title = '[COLOR green][LIVE NOW][/COLOR] {0}'.format(title)
    video.thumbnail = video_stream.get('thumbnailURL')

    if video_stream.get('entitlement'):
        video.subscription_required = True

    # Look for 'national' stream (e.g. Foxtel)
    video_id = get_attr(attrs, 'ooyala embed code')

    if not video_id:
        # Look for configured state stream
        state = ADDON.getSetting('STATE')
        video_id = get_attr(attrs, 'state-' + state)

    if not video_id:
        # Fall back to the VIC stream
        video_id = get_attr(attrs, 'state-VIC')

    if not video_id:
        utils.log('Unable to find video ID from stream data: {0}'.format(
                  video_data))
        raise exceptions.AussieAddonsException('Unable to find video '
                                               'ID from stream data.')

    video.ooyalaid = video_id
    video.live = True
    return video


def get_team_videos(team_id):
    url = config.VIDEO_LIST_URL + '?pageSize=50&teamIds=CD_T' + team_id
    return get_videos(url)


def get_category_videos(category):
    url = config.VIDEO_LIST_URL + '?categories=' + category
    return get_videos(url)


def get_round_videos(round_id):
    """Fetch the round and return the results"""
    url = config.ROUND_URL.format(round_id)
    return get_videos(url)


def get_videos(url):
    """Get videos from a given URL"""
    video_list = []
    data = fetch_url(url, request_token=True)
    try:
        json_data = json.loads(data)
    except ValueError:
        utils.log('Failed to load JSON. Data is: {0}'.format(data))
        raise Exception('Failed to retrieve video data. Service may be '
                        'currently unavailable.')

    for category in json_data['categories']:
        video_assets = category['videos']
        for video_asset in video_assets:
            video = parse_json_video(video_asset)
            if video:
                video_list.append(video)

    return video_list


def get_live_videos():
    video_list = []
    data = fetch_url(config.LIVE_LIST_URL, request_token=True)
    try:
        video_data = json.loads(data)
    except ValueError:
        utils.log('Failed to load JSON. Data is: {0}'.format(data))
        raise Exception('Failed to retrieve video data. Service may be '
                        'currently unavailable.')

    for video_asset in video_data:
        video = parse_json_live(video_asset)

        if video:
            video_list.append(video)

    #upcoming_videos = get_round('latest', True)
    #for match in upcoming_videos:
    #    v = classes.Video()
    #    v.title = match['name']
    #    v.isdummy = True
    #    v.url = 'null'
    #    video_list.append(v)
    return video_list


def get_seasons(season=None):
    """Grab the seasons/round list from the API"""
    data = json.loads(fetch_url(config.SEASONS_URL, request_token=True))
    seasons = data.get('seasons')
    if not season:
        return seasons
    for s in seasons:
        if s.get('id') == season:
            return s
