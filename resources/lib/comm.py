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
import custom_session
import datetime
import json
import time
import utils
import xbmcaddon

from exception import AFLVideoException

from bs4 import BeautifulStoneSoup

# Use local etree to get v1.3.0
import etree.ElementTree as ET

__addon__ = xbmcaddon.Addon()


def fetch_url(url, data=None, headers=None, request_token=False):
    """
    Simple function that fetches a URL using requests.
    An exception is raised if an error (e.g. 404) occurs.
    """
    utils.log("Fetching URL: %s" % url)
    with custom_session.Session() as session:

        if headers:
            session.headers.update(headers)

        # Token headers
        if request_token:
            update_token(session)

        if data:
            request = session.post(url, data)
        else:
            request = session.get(url)

        data = request.text
    return data


def update_token(session):
    """
        This functions performs a HTTP POST to the token URL
        and it will update the requests session with a token
        required for API calls
    """
    res = session.post(config.TOKEN_URL)
    try:
        token = json.loads(res.text).get('token')
    except Exception as e:
        raise AFLVideoException('Failed to retrieve API token: {0}\n'
                                'Service may be currently unavailable.'
                                ''.format(e))
    session.headers.update({'x-media-mis-token': token})


def get_attr(attrs, key):
    for attr in attrs:
        if attr.get('attrName') == key:
            return attr.get('attrValue')


def parse_json_video(video_data):
    """
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
        state = __addon__.getSetting('STATE')
        video_id = get_attr(attrs, 'state-' + state)

    if not video_id:
        # Fall back to the VIC stream
        video_id = get_attr(attrs, 'state-VIC')

    video.ooyalaid = video_id
    video.live = False
    return video


def parse_json_live(video_data):
    """
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
        state = __addon__.getSetting('STATE')
        video_id = get_attr(attrs, 'state-' + state)

    if not video_id:
        # Fall back to the VIC stream
        video_id = get_attr(attrs, 'state-VIC')

    if not video_id:
        utils.log('Unable to find video ID from stream data: {0}'.format(
                  video_data))
        raise AFLVideoException('Unable to find video ID from stream data.')

    video.ooyalaid = video_id
    video.live = True
    return video


def get_url_from_smil(data):
    soup = BeautifulStoneSoup(data)
    src = soup.find('video')['src']
    return src


def get_video(video_id):

    url = config.VIDEO_FEED_URL.format(video_id)
    data = fetch_url(url)

    json_data = json.loads(data)

    if len(json_data['entries']) == 0:
        raise IOError('Video URL not found')

    # Only one entry with this function
    video_data = json_data['entries'][0]
    video = parse_json_video(video_data)

    # Find our quality setting and fetch the URL
    qual = __addon__.getSetting('QUALITY')

    # Set the last video entry (usually highest qual) as a default fallback
    # in case we don't make a match below
    playlist = video_data['media$content'][0]['plfile$url']

    for video_entry in video_data['media$content']:
        # Match the video for the quality in the addon settings
        # The value should look like 1024000, but we only store 1024 in config
        if video_entry['plfile$bitrate'] == config.VIDEO_QUALITY[qual] * 1000:
            playlist = video_entry['plfile$url']

    smil = fetch_url(playlist)

    # Set the URL
    video.url = get_url_from_smil(smil)

    return video


def get_team_videos(team_id):
    url = config.VIDEO_LIST_URL + '?pageSize=50&teamIds=CD_T' + team_id
    return get_videos(url)


def get_category_videos(category):
    url = config.VIDEO_LIST_URL + '?categories=' + category
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

    upcoming_videos = get_round('latest', True)
    for match in upcoming_videos:
        v = classes.Video()
        v.title = match['name']
        v.isdummy = True
        v.url = 'null'
        video_list.append(v)
    return video_list


def get_round(round_id, live=False):
    """
        Fetch the round and return the results
    """
    round_matches = []
    round_url = config.ROUND_URL

    # Pass a 'latest' string in round_id to get 'this week'
    if round_id != 'latest':
        round_url = "%s/%s" % (round_url, round_id)

    xml = fetch_url(round_url)
    try:
        rnd = ET.fromstring(xml)
    except ET.ParseError:
        utils.log('Could not parse XML. Data is: {0}'.format(xml))
        raise Exception('Could not parse XML. Service may be '
                        'currently unavailable.')

    matches = rnd.find('matches').getchildren()

    for m in matches:
        d = dict(m.items())

        if d['homeSquadId']:
            match = {}
            home_team = utils.get_team(d['homeSquadId'])['name']
            away_team = utils.get_team(d['awaySquadId'])['name']
            match['name'] = "%s v %s" % (home_team, away_team)
            match['id'] = d['FixtureId']
            match['round_id'] = dict(rnd.items())['id']

            # special formatting for the 'upcoming games' list in the live menu
            if live:
                now = datetime.datetime.now()
                timestamp = d['dateTime']
                timezone = d['timezone']
                ts = datetime.datetime.fromtimestamp(
                    time.mktime(time.strptime(timestamp,
                                              "%Y-%m-%dT%H:%M:%S")))
                delta = now - ts
                # remove games that have already been played
                if delta > datetime.timedelta(hours=3):
                    continue
                airTime = ts.strftime(" - %A @ %I:%M %p A")
                match['name'] = '[COLOR red]{0}{1}{2}[/COLOR]'.format(
                                    match['name'], airTime, timezone)

            # Add date/time
            round_matches.append(match)

    return round_matches


def get_match_video(round_id, match_id, quality):

    match_video = []
    round_url = "%s/%s" % (config.ROUND_URL, round_id)

    try:
        xml = fetch_url(round_url)
        rnd = ET.fromstring(xml)

        matches = rnd.find('matches')
        match = matches.find('match[@FixtureId="%s"]' % match_id)

        qualities = match.find('qualities')
        quality = qualities.find('quality[@name="%s"]' %
                                 config.REPLAY_QUALITY[quality])
        periods = quality.find('periods')

        for qtr in periods.getchildren():
            qtr_dict = dict(qtr.items())
            match_video.append(qtr_dict)
    except Exception:
        return None

    return match_video
