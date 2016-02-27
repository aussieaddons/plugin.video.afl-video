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
#

import os
import re
import utils
import datetime
import urllib
import time
import config


class Video(object):

    def __init__(self):
        self.id = None
        self.title = ''
        self.genre = 'Sport'
        self.rating = 'PG'
        self.description = ''
        self.duration = 0
        self.season = None
        self.date = None
        self.thumbnail = None
        self.url = None

    def __repr__(self):
        return self.title

    def __cmp__(self, other):
        return cmp(self.title, other.title)

    def get_title(self):
        """ Return a string of the title, nicely formatted for XBMC list
        """
        return self.title

    def get_description(self):
        """ Return a string the program description, after running it through
            the descape.
        """
        return utils.descape(self.description)

    def get_genre(self):
        """ Return a string of the genre. E.g. Comedy
        """
        return utils.descape(self.genre)

    def get_rating(self):
        """ Return a string of the rating. E.g. PG, MA
        """
        return utils.descape(self.rating)

    def get_duration(self):
        """ Return a the duration of the video in seconds. This is only useful
             for the addStreamInfo method
        """
        seconds = int(self.duration)
        return seconds

    def get_date(self):
        """ Return a string of the date in the format 2010-02-28
            which is useful for XBMC labels.
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
        """ Returns the thumbnail
        """
        if self.thumbnail:
            thumb = utils.descape(self.thumbnail)
            thumb = thumb.replace(' ', '%20')
            return thumb
        return ''

    def get_url(self):
        return self.url

    def get_xbmc_list_item(self):
        """ Returns a dict of program information, in the format which
            XBMC requires for video metadata.
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

    def get_xbmc_stream_info(self):
        """
            Return a stream info dict
        """
        info_dict = {}
        if self.get_duration():
            info_dict['duration'] = self.get_duration()
        return info_dict

    def make_xbmc_url(self):
        """ Returns a string which represents the program object, but in
            a format suitable for passing as a URL.
        """
        d = {}
        if self.id:
            d['id'] = self.id
        if self.title:
            d['title'] = self.title
        if self.description:
            d['description'] = self.description
        if self.genre:
            d['genre'] = self.genre
        if self.duration:
            d['duration'] = self.duration
        if self.season:
            d['season'] = self.season
        if self.date:
            d['date'] = self.date.strftime("%Y-%m-%d %H:%M:%S")
        if self.thumbnail:
            d['thumbnail'] = self.thumbnail
        if self.url:
            d['url'] = self.url

        return utils.make_url(d)

    def parse_xbmc_url(self, string):
        """ Takes a string input which is a URL representation of the
            program object
        """
        d = utils.get_url(string)
        if 'id' in d:
            self.id = d.get('id')
        if 'title' in d:
            self.title = d.get('title')
        if 'description' in d:
            self.description = d.get('description')
        if 'genre' in d:
            self.genre = d.get('genre')
        if 'season' in d:
            self.season = d.get('season')
        if 'duration' in d:
            self.duration = d.get('duration')
        if 'url' in d:
            self.url = urllib.unquote_plus(d.get('url'))
        if 'thumbnail' in d:
            self.thumbnail = urllib.unquote_plus(d.get('thumbnail'))
        if 'date' in d:
            ts = time.strptime(d.get('date'), '%Y-%m-%d %H:%M:%S')
            timestamp = time.mktime(ts)
            self.date = datetime.date.fromtimestamp(timestamp)
