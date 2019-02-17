#
#    AFL Video Kodi Add-on
#    Copyright (C) 2016 Andy Botting
#
#    AFL Video is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    AFL Video is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this add-on. If not, see <http://www.gnu.org/licenses/>.

# Ignore flake8 E501 line too long
# flake8: noqa

# These values match the bitrate given in the video data
VIDEO_QUALITY = {'0': 172,
                 '1': 1024,
                 '2': 2048}

# These are the strings used for selecting quality via the smart replay system.
REPLAY_QUALITY = {'0': 'low',
                  '1': 'med',
                  '2': 'high'}

# Maximum video quality for Ooyala m3u8 playlists.
MAX_LIVE_QUAL = 4
MAX_REPLAY_QUAL = 6


USER_AGENT = 'Dalvik/2.1.0 (Linux; U; Android 6.0; HTC One_M8 Build/MRA58K.H15)'
USER_AGENT_LONG = 'Mozilla/5.0 (Linux; Android 6.0; HTC One_M8 Build/MRA58K.H15; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/56.0.2924.87 Mobile Safari/537.36'

# Round URL, which lists the games of the round if they've had their Videos uploaded
# This URL can also take a 'Round ID' added to the end (e.g CD_R201301401)
ROUND_URL = 'https://api.afl.com.au/cfs/afl/videos/round/{0}?pageSize=50&pageNum=1&categories=Match%20Replays&includeOnlineVideos=false'

# This URL returns a token if POST'ed to. The token is required in the header to any
# reqeusts against the API
TOKEN_URL = 'http://api.afl.com.au/cfs/afl/WMCTok'

# API URL for all seasons and rounds data
SEASONS_URL = 'https://api.afl.com.au/cfs/afl/seasons'

# API URL for fixture data
FIXTURE_URL = 'https://api.afl.com.au/cfs/afl/fixturesAndResults/season/{0}/round/{1}'

# API URL for current live videos
LIVE_LIST_URL = 'http://api.afl.com.au/cfs/afl/liveMedia?org=AFL&view=full'

VIDEO_LIST_URL = 'https://api.afl.com.au/cfs/afl/videos'

# Bigpond authentication URL
LOGIN_URL = 'https://services.bigpond.com/rest/v1/AuthenticationService/authenticate'

# This URL returns our user ID after authentication
SESSION_URL = 'http://api.sub.afl.com.au/cfs-premium/users/session?sessionId={0}'

# URL to retrieve Ooyala embed token from
EMBED_TOKEN_URL = 'https://api.afl.com.au/cfs/users/{0}/token?embedCode={1}'

# URL to send our embed token and retrieve playlist
AUTH_URL = 'http://player.ooyala.com/sas/player_api/v1/authorization/embed_code/{0}/{1}?device=html5&domain=http://www.ooyala.com&supportedFormats=m3u8'

# Ooyala provider indentifier code used in contructing request uris
PCODE = 'Zha2IxOrpV-sPLqnCop1Lz0fZ5Gi'

# http headers required for accessing Bigpond authentication URL
HEADERS = {'User-Agent' : USER_AGENT,
           'Authorization': 'Basic QUZMb3dfZGV2aWNlOmFOVSNGNHJCU0dqbmtANEZXM0Zt',
           'Content-Type': 'application/x-www-form-urlencoded'}

VIDEO_FEED_URL = "http://feed.theplatform.com/f/gqvPBC/AFLProd_Online_H264?byGuid={0}&form=json"

# AFLW

AFLW_INDEX_URL = 'https://app-league-aflw.yinzcam.com/V1/Home/Index?carrier=&height=1776&ycurl_version=1&os=Android&platform=Android&mnc=0&ff=mobile&app_version=1.0.5&version=5.7&width=1080&mcc=0&os_version=7.1.2&application=AFLW_LEAGUE'

AFLW_BOX_URL = 'https://app-league-aflw.yinzcam.com/V1/Game/Box/{0}?carrier=&height=1776&error=100000000&ycurl_version=1&os=Android&a=0&platform=Android&mnc=0&ff=mobile&b=0&app_version=1.0.5&version=5.7&width=1080&mcc=0&os_version=7.1.2&application=AFLW_LEAGUE'

AFLW_SCORE_URL = 'https://app-league-aflw.yinzcam.com/V1/Game/Scores/?carrier=&height=1776&ycurl_version=1&os=Android&platform=Android&ff=mobile&mnc=0&app_version=1.0.5&version=5.7&width=1080&os_version=7.1.2&mcc=0&application=AFLW_LEAGUE&compId=CD_S2018264'

AFLW_LONG_URL = 'https://app-league-aflw.yinzcam.com/V1/Media/LongList?carrier=&height=1776&ycurl_version=1&os=Android&platform=Android&mnc=0&ff=mobile&app_version=1.0.5&version=5.7&width=1080&mcc=0&os_version=7.1.2&application=AFLW_LEAGUE'

# New auth config for 2017

AFL_LOGIN_URL = 'http://api.sub.afl.com.au/cfs-premium/users?paymentMethod=ONE_PLACE'

SIGNON_HEADERS = {'Connection': 'keep-alive',
                  'Cache-Control': 'max-age=0',
                  'Origin': 'https://signon.telstra.com.au',
                  'Upgrade-Insecure-Requests': '1',
                  'User-Agent': USER_AGENT_LONG,
                  'Content-Type': 'application/x-www-form-urlencoded',
                  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                  'Accept-Encoding': 'gzip,deflate',
                  'Accept-Language': 'en-AU,en-US;q=0.8'}

SIGNON_URL = 'https://signon.telstra.com.au/login'

OLD_OFFERS_URL = 'https://api.telstra.com/v1/media-products/catalogues/media/offers?category=afl'

OFFERS_URL = 'https://tapi.telstra.com/v1/media-products/catalogues/media/offers'

HUB_URL = 'http://hub.telstra.com.au/sp2017-afl-app'

MEDIA_ORDER_HEADERS = {'Content-Type': 'application/json',
                       'Accept': 'application/json, text/plain, */*',
                       'Connection': 'keep-alive',
                       'Origin': 'https://hub.telstra.com.au',
                       'User-Agent': USER_AGENT_LONG,
                       'Accept-Encoding': 'gzip, deflate',
                       'Accept-Language': 'en-AU,en-US;q=0.8',
                       'X-Requested-With': 'com.telstra.android.afl'}

OLD_MEDIA_ORDER_URL = 'https://api.telstra.com/v1/media-commerce/orders'

MEDIA_ORDER_URL = 'https://tapi.telstra.com/v1/media-commerce/orders'

MEDIA_ORDER_JSON = '{{"serviceId":"{0}","serviceType":"MSISDN","offer":{{"id":"{1}"}},"pai":"{2}"}}'

SPORTSPASS_URL = 'http://hub.telstra.com.au/sp2017-afl-app?tpUID={0}&type=SportPassConfirmation&offerId=a482eaad-9213-419c-ace2-65b7cae73317'

SSO_URL = 'https://tapi.telstra.com/v1/sso/auth'

SSO_PARAMS = {'redirect_uri': 'https://hub.telstra.com.au/offers/content/cached/callback.html',
              'response_type': 'id_token token',
              'scope': 'openid email profile phone telstra.user.sso.profile'}
              
SSO_HEADERS = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, '
                                  'deflate',
               'Accept-Language': 'en-AU,en-US;q=0.9',
               'Cache-Control': 'max-age=0',
               'Connection': 'keep-alive',
               'X-Requested-With': 'com.telstra.android.afl'}

SPC_HEADERS = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Encoding': 'gzip, '
                                  'deflate',
               'Accept-Language': 'en-AU,en-US;q=0.9',
               'User-Agent': USER_AGENT_LONG,
               'X-Requested-With': 'com.telstra.android.afl'}

#Mobile Auth
OFFER_ID = 'a482eaad-9213-419c-ace2-65b7cae73317'

OAUTH_HEADERS = {'User-Agent': 'AFL(Android) / 40656',
                 'Accept-Encoding': 'gzip'}

OAUTH_URL = 'https://api.telstra.com/v1/media-commerce/oauth/token'

MOBILE_ID_URL = 'http://medrx.telstra.com.au/online.php'

MOBILE_CLIENT_ID = 'BDm2sYxE5twDWsM5CXAWHUPrm1ultZ9L'

MOBILE_CLIENT_SECRET = 'uIGtb1DTQ0LBxe1N'

MOBILE_TOKEN_PARAMS = {'client_id': MOBILE_CLIENT_ID,
                      'client_secret': MOBILE_CLIENT_SECRET,
                      'grant_type': 'client_credentials',
                      'scope': 'MEDIA-PRODUCTS-API MEDIA-COMMERCE-API',
                      'x-user-idp': 'NGP'}

MOBILE_ORDER_JSON = {"offer": {"id":OFFER_ID}, "serviceType":"MSISDN"}

# Categories existing on the new content system

CATEGORIES = [
    'Live Matches',
    'Team Video',
    'Recent Match Replays',
    'All Match Replays',
    'AFLW',
    'Auto-generated Highlights',
    'Editorial Highlights',
    'Media Conferences',
    'Match Day',
    'Shows',
    'Mark and Goal',
    'News',
    'All',
    'Settings'
]

CATEGORY_LOOKUP = {
    'Live Matches': 'Live Matches',
    'Team Video': 'Team Video',
    'Recent Match Replays': 'Match Replays&pageSize=50',
    'All Match Replays': 'All Match Replays',
    'Auto-generated Highlights': 'Auto-generated Highlights&pageSize=50',
    'Editorial Highlights': 'Editorial Highlights&pageSize=50',
    'Media Conferences': 'Media Conferences&pageSize=50',
    'Match Day': 'The 10,Auto-generated Highlights,Media Conferences',
    'Shows': 'Access All Areas,The 10,Where It All Began,Pick A Winner,Friday Front Bar,In the moment,Versus,Round Rewind,Special Features',
    'Mark and Goal': 'Mark of the Year,Goal of the Year&pageSize=20',
    'News': 'News&pageSize=50',
    'All': 'all&pageSize=50',
    'Settings': 'Settings'
}

# Channel is used for Bigpond Video and Squad is used in Round XML
# http://www.afl.com.au/api/gas/afl/squad
TEAMS = [
    {'id': '1',  'name': 'Adelaide',               'team_id': '10',   'thumb': 'adel.png'},
    {'id': '2',  'name': 'Brisbane',               'team_id': '20',   'thumb': 'bris.png'},
    {'id': '3',  'name': 'Carlton',                'team_id': '30',   'thumb': 'carl.png'},
    {'id': '4',  'name': 'Collingwood',            'team_id': '40',   'thumb': 'coll.png'},
    {'id': '5',  'name': 'Essendon',               'team_id': '50',   'thumb': 'ess.png'},
    {'id': '6',  'name': 'Fremantle',              'team_id': '60',   'thumb': 'frem.png'},
    {'id': '7',  'name': 'Gold Coast',             'team_id': '1000', 'thumb': 'gcfc.png'},
    {'id': '8',  'name': 'Geelong',                'team_id': '70',   'thumb': 'geel.png'},
    {'id': '9',  'name': 'Greater Western Sydney', 'team_id': '1010', 'thumb': 'gws.png'},
    {'id': '10', 'name': 'Hawthorn',               'team_id': '80',   'thumb': 'haw.png'},
    {'id': '11', 'name': 'Melbourne',              'team_id': '90',   'thumb': 'melb.png'},
    {'id': '12', 'name': 'North Melbourne',        'team_id': '100',  'thumb': 'nmfc.png'},
    {'id': '13', 'name': 'Port Adelaide',          'team_id': '110',  'thumb': 'port.png'},
    {'id': '14', 'name': 'Richmond',               'team_id': '120',  'thumb': 'rich.png'},
    {'id': '15', 'name': 'St. Kilda',              'team_id': '130',  'thumb': 'stk.png'},
    {'id': '16', 'name': 'Sydney',                 'team_id': '160',  'thumb': 'syd.png'},
    {'id': '17', 'name': 'West Coast',             'team_id': '150',  'thumb': 'wce.png'},
    {'id': '18', 'name': 'Western Bulldogs',       'team_id': '140',  'thumb': 'wb.png'},
]
