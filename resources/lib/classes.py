import datetime
import time
import unicodedata
from builtins import str
from collections import OrderedDict

from future.moves.urllib.parse import parse_qsl, quote_plus, unquote_plus

from aussieaddonscommon import utils


class Video(object):

    def __init__(self):
        self.video_id = None
        self.title = ''
        self.genre = 'Sport'
        self.rating = 'PG'
        self.description = ''
        self.duration = 0
        self.season = None
        self.date = None
        self.thumbnail = None
        self.url = None
        self.ooyalaid = None
        self.isdummy = None
        self.live = None
        self.type = None
        self.account_id = None
        self.policy_key = None
        self.subscription_required = False

    def __repr__(self):
        return self.title

    def __cmp__(self, other):
        return cmp(self.title, other.title)

    def get_title(self):
        """Return a string of the title, nicely formatted for Kodi list"""
        return self.title

    def get_description(self):
        """Return a string the program description"""
        if self.description:
            return utils.descape(self.description)
        else:
            return self.get_title()

    def get_genre(self):
        """Return a string of the genre. E.g. Sport"""
        return utils.descape(self.genre)

    def get_rating(self):
        """Return a string of the rating. E.g. PG, MA"""
        return utils.descape(self.rating)

    def get_duration(self):
        """Return a the duration of the video in seconds."""
        seconds = int(self.duration)
        return seconds

    def get_date(self):
        """Get date

        Return a string of the date in the format 2010-02-28 which is useful
        for Kodi labels.
        """
        if self.date:
            return self.date.strftime("%Y-%m-%d")
        return None

    def get_season(self):
        season = datetime.datetime.now().year
        if self.season:
            season = self.season
        return season

    def get_thumbnail(self):
        """Returns the thumbnail"""
        if self.thumbnail:
            thumb = utils.descape(self.thumbnail)
            thumb = thumb.replace(' ', '%20')
            return thumb
        return ''

    def get_url(self):
        return self.url

    def get_kodi_list_item(self):
        """Get XBMC list item

        Returns a dict of program information, in the format which
        Kodi requires for video metadata.
        """
        info_dict = {}
        if self.get_title():
            info_dict['title'] = self.get_title()
        if self.get_description():
            info_dict['plot'] = self.get_description()
        if self.get_genre():
            info_dict['genre'] = self.get_genre()
        if self.get_date():
            info_dict['aired'] = self.get_date()
        if self.get_season():
            info_dict['season'] = self.get_season()
        return info_dict

    def get_kodi_stream_info(self):
        """Return a stream info dict"""
        info_dict = {}
        if self.get_duration():
            info_dict['duration'] = self.get_duration()
        return info_dict

    def make_kodi_url(self):
        d_original = OrderedDict(
            sorted(self.__dict__.items(), key=lambda x: x[0]))
        d = d_original.copy()
        for key, value in d_original.items():
            if not value:
                d.pop(key)
                continue
            if isinstance(value, str):
                d[key] = unicodedata.normalize(
                    'NFKD', value).encode('ascii', 'ignore').decode('utf-8')
        url = ''
        for key in d.keys():
            if isinstance(d[key], (str, bytes)):
                val = quote_plus(d[key])
            else:
                val = d[key]
            url += '&{0}={1}'.format(key, val)
        url += '&addon_version={0}'.format(utils.get_addon_version())
        return url

    def parse_kodi_url(self, url):
        params = dict(parse_qsl(url))
        params.pop('addon_version', '')
        for item in params.keys():
            setattr(self, item, unquote_plus(params[item]))
        if self.date:
            try:
                self.date = datetime.datetime.strptime(self.date, "%Y-%m-%d")
            except TypeError:
                self.date = datetime.datetime(
                    *(time.strptime(self.date, "%Y-%m-%d")[0:6]))
