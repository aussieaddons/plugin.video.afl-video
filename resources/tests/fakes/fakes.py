# coding=utf-8
try:
    basestring
except NameError:
    basestring = str

import xbmcaddon

import xbmcgui


class FakeAddon(xbmcaddon.Addon):
    def __init__(self, sub_type, username='foo', password='bar',
                 iap_token='aabbccddeeff00112233445566778899',
                 live_sub='true'):
        super(FakeAddon, self).__init__()
        self.SUBSCRIPTION_TYPE = sub_type
        self.LIVE_USERNAME = username
        self.LIVE_PASSWORD = password
        self.LIVE_SUBSCRIPTION = live_sub
        self.IAP_TOKEN = iap_token

    def getSetting(self, setting):
        return getattr(self, setting, '')


class FakeListItem(xbmcgui.ListItem):
    def __init__(self, label="", label2="", iconImage="", thumbnailImage="",
                 path="", offscreen=False):
        super(FakeListItem, self).__init__()
        self.setLabel(label)
        self.setLabel2(label2)
        self.setIconImage(iconImage)
        self.setThumbnailImage(thumbnailImage)
        self.setPath(path)
        self.offscreen = offscreen
        self.art = {}
        self.defaultRating = ''
        self.info = {}
        self.rating = {}
        self.streamInfo = {}
        self.property = {}
        self.subtitles = None
        self.uniqueid = {}

    def setLabel(self, label):
        assert isinstance(label, basestring)
        self.label = label

    def setLabel2(self, label):
        self.label2 = label

    def setIconImage(self, iconImage):
        self.iconImage = iconImage

    def setThumbnailImage(self, thumbFilename):
        self.thumbFilename = thumbFilename

    def setArt(self, dictionary):
        allowed_keys = [
            'thumb',
            'poster',
            'banner',
            'fanart',
            'clearart',
            'clearlogo',
            'landscape',
            'icon'
        ]
        for k, v in dictionary.items():
            if k not in allowed_keys:
                raise Exception('Unallowed key for setArt')
            self.art.update({k: v})

    def setIsFolder(self, isFolder):
        assert type(isFolder) == bool
        self.is_folder = isFolder

    def setUniqueIDs(self, values, defaultrating=''):
        allowed_keys = [
            'imdb',
            'tvdb',
            'tmdb',
            'anidb'
        ]
        if defaultrating:
            assert defaultrating in allowed_keys
            self.defaultRating = defaultrating
        for k, v in values.items():
            assert k in allowed_keys
            self.uniqueid.update({k: v})

    def setRating(self, type, rating, votes=0, default=False):
        assert isinstance(type, basestring)
        assert isinstance(rating, (int, float))
        assert isinstance(votes, int)
        assert isinstance(default, bool)
        self.rating.update({'type': type, 'rating': rating, 'votes': votes,
                            'default': default})

    def addSeason(self, number, name=''):
        assert isinstance(number, int)
        assert isinstance(name, basestring)

    def setInfo(self, type, infoLabels):
        self.info.update(infoLabels)

    def addStreamInfo(self, cType, dictionary):
        self.streamInfo.update({cType: dictionary})

    def setProperty(self, key, value):
        self.property.update({key: value})

    def setProperties(self, dictionary):
        self.property.update(dictionary)

    def setPath(self, path):
        assert isinstance(path, (str))
        self.path = path

    def setSubtitles(self, subtitleFiles):
        assert isinstance(subtitleFiles, (str))
        self.subtitles = subtitleFiles

    def getLabel(self):
        return self.label

    def getPath(self):
        return self.path


class FakePlugin(object):
    def __init__(self):
        self.SORT_METHOD_LABEL = 1
        self.SORT_METHOD_LABEL_IGNORE_THE = 2
        self.SORT_METHOD_NONE = 0
        self.SORT_METHOD_TITLE = 9
        self.SORT_METHOD_TITLE_IGNORE_THE = 10
        self.SORT_METHOD_UNSORTED = 40
        self.SORT_METHOD_VIDEO_SORT_TITLE = 26
        self.SORT_METHOD_VIDEO_SORT_TITLE_IGNORE_THE = 27
        self.SORT_METHOD_VIDEO_TITLE = 25
        self.directory = []

    def addDirectoryItem(self, handle, url, listitem, isFolder=False,
                         totalItems=0):
        assert isinstance(url, (str))
        self.directory.append(
            {'handle': handle, 'url': url, 'listitem': listitem,
             'isFolder': isFolder})

    def addDirectoryItems(self, handle, items, totalItems=0):
        for item in items:
            self.addDirectoryItem(handle, item[0], item[1],
                                  item[2] if len(item) == 3 else False,
                                  totalItems)

    def endOfDirectory(self, handle, succeeded=True, updateListing=False,
                       cacheToDisc=True):
        self.end = True

    def setResolvedUrl(self, handle, succeeded, listitem):
        self.resolved = (handle, succeeded, listitem)

    def addSortMethod(self, handle, sortMethod, label2Mask=''):
        pass

    def setContent(self, handle, content):
        self.content = content


MIS_UUID = 'mis-uuid-aabbccddeeff00112233445566778899'

COMPLETED_MATCH_ID = '20191111610'

FAKE_VIDEO_ATTRS = {
    'video_id': '12345',
    'thumb': 'https://foo.com/bar.jpg',
    'title': 'FooBar',
    'live': True,
    'time': '2019-07-07T03:00:00Z',
    'desc': 'Game of foo vs bar',
    'dummy': 'None',
    'link_id': 'None'
}

FAKE_VIDEO_URL = '&desc=Game+of+foo+vs+bar&dummy=None&genre=Sport&link_id' \
                 '=None&live=True&rating=PG&thumb=https%3A%2F%2Ffoo.com' \
                 '%2Fbar.jpg&time=2019-07-07T03%3A00%3A00Z&title=FooBar' \
                 '&video_id=12345'

M3U8_URL_OOYALA = {
    'stream_url': 'http://player.ooyala.com/player/iphone'
                  '/1yNGE5dDoyTdUKykqSeTysvmgup-rvS1.m3u8',
    'widevine_url': ''}

M3U8_URL_BC = {
    'stream_url': 'https://foo.bar/index.m3u8',
    'widevine_url': ''}

VIDEO_ID = '1yNGE5dDoyTdUKykqSeTysvmgup-rvS1'

# telstra_auth

FAKE_XSRF_COOKIE = 'XSRF-TOKEN=foobar; path=/; secure'

FAKE_BPSESSION_COOKIE = 'BPSESSION=AQICapYHjH4f; Domain=telstra.com.au; ' \
                        'Path=/; HttpOnly; Secure'

FAKE_UUID = [
    'e8485af7-fe81-4064-bfb0-fdafbf68db33',
    'cea23fb2-ab9d-4869-8b01-fdb66aab09e7'
]

FAKE_RANDOM = [
    b'\xb7\x91e|\x7fd\x1e\xdal\x8b\x99\xe2Z\xf2\xe9Y',
    b'\x11\x7ff(\x01\n\xf7\x13lHq\xcb\xfa\x81\x03\xf3'
]

MYID_RESUME_AUTH_REDIRECT_URL = \
    'https://hub.telstra.com.au/offers/content/cached/callback.html?code' \
    '=Hg_CHduWoq-xFg3CCH1N30n05ItFXAde6x1SldNB&state' \
    '=2cbb648bedfa77b8751a603994164fee'

FAKE_MOBILE_COOKIE = 'GUID_S=12345678901; path=/; secure'

FAKE_MOBILE_COOKIE_NO_DATA = 'nouid=124.171.69.58; path=/; secure'
