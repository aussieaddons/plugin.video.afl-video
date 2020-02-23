import datetime
import json
import time
import xml.etree.ElementTree as ET

from future.moves.urllib.parse import quote_plus

from aussieaddonscommon import exceptions
from aussieaddonscommon import session
from aussieaddonscommon import utils

from resources.lib import classes
from resources.lib import config

import xbmcaddon

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
        request.encoding = 'utf-8-sig'
        if request.text[0] == u'\ufeff':  # bytes \xef\xbb\xbf in utf-8 encding
            request.encoding = 'utf-8-sig'
        data = request.text
    return data.encode('utf-8')


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


def get_bc_url(video):
    config_data = json.loads(fetch_url(config.CONFIG_URL, request_token=True))

    video.policy_key = [x for x in config_data['general'] if
                        x.get('id') == 'brightCovePK_premium'][0].get('value')
    video.account_id = [x for x in config_data['general'] if
                        x.get('id') == 'brightCoveAccountId'][0].get('value')

    if not video.policy_key:
        raise Exception("Can't retrieve brightcove policy key for {0}".format(
            video.account_id))
    data = fetch_url(config.BC_EDGE_URL.format(account_id=video.account_id,
                                               video_id=video.video_id),
                     headers={'BCOV-POLICY': video.policy_key})
    json_data = json.loads(data)
    src = None
    for source in json_data.get('sources'):
        if source.get('type') == 'application/vnd.apple.mpegurl':
            src = source.get('src')
    if not src:
        utils.log(json_data.get('sources'))
        raise Exception('Unable to locate video source.')
    return src


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
    video.video_id = get_attr(attrs, 'brightcove video id')
    if video.video_id:
        video.type = 'B'
    else:
        video.video_id = get_attr(attrs, 'ooyala embed code')
        video.type = 'O'
    video.live = False
    return video


def parse_json_live(video_data):
    """Parse JSON live stream data

    Parse the JSON data for live match and construct a video object from it
    for a list of videos
    """
    streams = video_data.get('videoStreams')
    video_stream = None
    for stream in streams:
        for attrib in stream.get('customAttributes'):
            if attrib.get('attrName') == 'brightcove_videoid':
                video_stream = stream
                break
        if video_stream:
            break
    if not video_stream:
        return

    attrs = video_stream.get('customAttributes')

    video = classes.Video()
    title = utils.ensure_ascii(video_data.get('title'))
    video.title = '[COLOR green][LIVE NOW][/COLOR] {0}'.format(title)
    video.thumbnail = get_attr(attrs, 'imageURL')

    if get_attr(attrs, 'entitlement') == 'true':
        video.subscription_required = True

    # Look for 'national' stream (e.g. Foxtel)
    video_id = get_attr(attrs, 'brightcove_videoid')
    utils.log(video_id)
    if not video_id:
        utils.log('Unable to find video ID from stream data: {0}'.format(
                  video_data))
        raise exceptions.AussieAddonsException('Unable to find video '
                                               'ID from stream data.')

    video.video_id = video_id
    video.live = True
    video.type = 'B'
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
        video_data = json.loads(data).get('content')
    except ValueError:
        utils.log('Failed to load JSON. Data is: {0}'.format(data))
        raise Exception('Failed to retrieve video data. Service may be '
                        'currently unavailable.')

    for video_asset in video_data:
        video = parse_json_live(video_asset)

        if video:
            video_list.append(video)

    video_list += get_upcoming()
    video_list += get_aflw_upcoming()
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


def get_upcoming():
    """Make a dummy file list for users to see upcoming matches/times"""
    season_data = json.loads(fetch_url(config.SEASONS_URL, request_token=True))
    current_season = season_data.get('currentSeasonId')
    current_round = None
    for s in season_data.get('seasons'):
        if s.get('id') == current_season:
            current_round = s.get('currentRoundId')
            break

    if not current_round:
        return None

    fixture_url = config.FIXTURE_URL.format(current_season, current_round)
    fixture_data = json.loads(fetch_url(fixture_url, request_token=True))

    listing = []
    for match in fixture_data.get('fixtures'):
        if match.get('status') in ['SCHEDULED',
                                   'UNCONFIRMED_TEAMS',
                                   'CONFIRMED_TEAMS']:
            v = classes.Video()
            try:
                home = match['homeTeam'].get('teamName')
                away = match['awayTeam'].get('teamName')
            except KeyError:
                continue
            match_time = get_airtime(match.get('utcStartTime'))
            title = '{home} vs {away} - {time}'
            v.title = title.format(home=home, away=away, time=match_time)
            v.isdummy = True
            v.url = 'null'
            listing.append(v)
    return listing


def get_airtime(timestamp, aflw=False):
    """Convert timestamp to nicely formatted local time"""
    try:
        delta = ((time.mktime(time.localtime()) -
                 time.mktime(time.gmtime())) / 3600)
        if time.localtime().tm_isdst:
            delta += 1
        ts_format = "%Y-%m-%dT%H:%M:%S.000+0000"
        if aflw:
            ts_format = ts_format.replace('.000+0000', 'Z')
        ts = datetime.datetime.fromtimestamp(
            time.mktime(time.strptime(timestamp, ts_format)))
        ts += datetime.timedelta(hours=delta)
        return ts.strftime("%A %d %b @ %I:%M %p").replace(' 0', ' ')
    except OverflowError:
        return timestamp

# AFLW functions


def get_aflw_upcoming():
    """
    similar to get_score but this time we are searching for upcoming live
    match info
    """
    data = fetch_url(config.AFLW_SCORE_URL)
    tree = ET.fromstring(data)
    listing = []

    for elem in tree.findall("Day"):
        for subelem in elem.findall("Game"):
            if subelem.find('GameState').text == 'COMPLETE':
                continue
            v = classes.Video()
            home = subelem.find('HomeTeam').attrib['FullName']
            away = subelem.find('AwayTeam').attrib['FullName']
            timestamp = subelem.find('Timestamp').text
            # convert zulu to local time
            airtime = get_airtime(timestamp, aflw=True)
            title = ('[COLOR red]AFLW:[/COLOR] '
                     '{0} vs {1} - {2}')
            v.title = title.format(home, away, airtime)
            v.dummy = True
            listing.append(v)
    return listing


def get_aflw_score(match_id):
    """
    fetch score xml and return the scores for corresponding match IDs
    """
    data = fetch_url(config.AFLW_SCORE_URL)
    tree = ET.fromstring(data)

    for elem in tree.findall("Day"):
        for subelem in elem.findall("Game"):
            if subelem.attrib['Id'] == str(match_id):
                home_score = str(subelem.find('HomeTeam').attrib['Score'])
                away_score = str(subelem.find('AwayTeam').attrib['Score'])
                return '[COLOR yellow]{0} - {1}[/COLOR]'.format(
                    home_score, away_score)


def get_aflw_videos():
    data = fetch_url(config.AFLW_LONG_URL)
    tree = ET.fromstring(data)
    listing = []

    for elem in tree.findall('MediaSection'):
        for video in elem.findall('Item'):
            if video.attrib['Type'] == 'V':
                v = classes.Video()
                v.title = video.find('Title').text
                v.thumbnail = video.find('FullImageUrl').text
                v.type = video.find('Video').attrib['Type']
                v.video_id = video.find('Video').attrib['Id']
                v.policy_key = video.find('Video').attrib['PolicyKey']
                v.account_id = video.find('Video').attrib['AccountId']
                listing.append(v)
    return listing


def find_aflw_live_matches():
    """
    get index of current round's games so we can find the 'box' URL
    and make a list of game ids,
    returns a list of ElementTree objects to parse for live matches
    """
    data = fetch_url(config.AFLW_INDEX_URL)
    tree = ET.fromstring(data)
    box_list = []
    listing = []

    for elem in tree.find('HeadlineGames'):
        box_list.append(elem.attrib['Id'])

    for game_id in box_list:
        data = fetch_url(config.AFLW_BOX_URL.format(game_id))
        tree = ET.fromstring(data)
        watch_button = tree.find('WatchButton')
        if watch_button is not None:
            if watch_button.find('Title').text != 'WATCH REPLAY':
                listing.append(tree)
    return listing


def get_stream_url(video, embed_token):
    src = get_bc_url(video)
    if not embed_token:
        return str(src)
    else:
        src = sign_url(src, embed_token)
    return src


def sign_url(url, media_auth_token):
    headers = {'authorization': 'JWT {0}'.format(media_auth_token)}
    data = json.loads(
        fetch_url(config.SIGN_URL.format(quote_plus(url)), headers=headers))
    if data.get('message') == 'SUCCESS':
        return str(data.get('url'))
    else:
        raise Exception('error in signing url')
