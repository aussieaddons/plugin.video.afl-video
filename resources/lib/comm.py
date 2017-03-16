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
import requests
import time
import urllib
import utils
import xbmcaddon

from requests.adapters import HTTPAdapter
from bs4 import BeautifulStoneSoup

# Use local etree to get v1.3.0
import etree.ElementTree as ET


def fetch_url(url, request_token=False):
    """
    Simple function that fetches a URL using requests.
    An exception is raised if an error (e.g. 404) occurs.
    """
    utils.log("Fetching URL: %s" % url)
    with requests.Session() as session:
        session.mount('http://', HTTPAdapter(max_retries=5))
        session.mount('https://', HTTPAdapter(max_retries=5))
        # Token headers
        if request_token:
            update_token(session)

        request = session.get(url, verify=False)
        request.raise_for_status()
        data = request.text
    return data


def update_token(session):
    """
        This functions performs a HTTP POST to the token URL
        and it will update the requests session with a token
        required for API calls
    """
    res = requests.post(config.TOKEN_URL)
    try:
        token = json.loads(res.text).get('token')
    except Exception as e:
        raise Exception('Failed to retrieve API token: {0} '
                        'Service may be currently unavailable.'.format(e))
    session.headers.update({'x-media-mis-token': token})


def parse_json_video(video_data):
    """
        Parse the JSON data and construct a video object from it for a list
        of videos
    """
    # Find our quality setting and fetch the URL
    __addon__ = xbmcaddon.Addon()
    qual = __addon__.getSetting('QUALITY')

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

    data = video_data.get('customAttributes')
    video.ooyalaid = [x['attrValue'] for x in data if x['attrName'] == 'ooyala embed code'][0]
    video.live = False

    return video

def parse_json_live(video_data):
    """
        Parse the JSON data for live match and construct a video object from it
        for a list of videos
    """
    if not video_data['videoStream']:
        return

    if 'customAttributes' not in video_data['videoStream']:
        return

    video = classes.Video()
    title = utils.ensure_ascii(video_data.get('title'))
    video.title = '[COLOR green][LIVE NOW][/COLOR] {0}'.format(title)
    video.description = title
    video.thumbnail = video_data['videoStream'].get('thumbnailURL')
    atrbs = video_data['videoStream'].get('customAttributes')
    id = [x['attrValue'] for x in atrbs if x['attrName'] == 'ooyala embed code']
    video.ooyalaid = id[0]
    video.live = True

    return video


def get_url_from_smil(data):
    soup = BeautifulStoneSoup(data)
    src = soup.find('video')['src']
    return src


def get_video(video_id):

    url = "http://feed.theplatform.com/f/gqvPBC/AFLProd_Online_H264?byGuid=%s&form=json" % video_id
    data = fetch_url(url)

    json_data = json.loads(data)

    if len(json_data['entries']) == 0:
        raise IOError('Video URL not found')

    # Only one entry with this function
    video_data = json_data['entries'][0]
    video = parse_json_video(video_data)

    # Find our quality setting and fetch the URL
    __addon__ = xbmcaddon.Addon()
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


def get_videos(category):
    """
        Get all videos by category
    """
    video_list = []

    # Category names are URL encoded
    if category == 'All Videos':
        url = config.VIDEO_LIST_URL
    elif category == 'Live Matches':
        url = config.LIVE_LIST_URL
    else:
        url = config.VIDEO_LIST_URL + '?categories=' + category

    data = fetch_url(url, request_token=True)
    try:
        json_data = json.loads(data)
    except ValueError:
        utils.log('Failed to load JSON. Data is: {0}'.format(data))
        raise Exception('Failed to retrieve video data. Service may be '
                        'currently unavailable.')

    if category == 'Live Matches':
        video_assets = json_data

        for video_asset in video_assets:
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

    else:
        for category in json_data['categories']:
            video_assets = category['videos']
            for video_asset in video_assets:
                video = parse_json_video(video_asset)
                if video:
                    video_list.append(video)

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
