import os
import re
import utils
import datetime
import urllib
import time
import config

#import xbmcaddon
#__addon__ = xbmcaddon.Addon(os.path.basename(os.getcwd()))


class Video(object):

	def __init__(self):
		self.id = -1
		self.title = ''
		self.category = 'Sport'
		self.keywords = []
		self.rating = 'PG'
		self.description = None
		self.duration = None
		self.season = None
		self.date = datetime.datetime.now()
		self.thumbnail = None

	def __repr__(self):
		return self.title

	def __cmp__(self, other):
		return cmp(self.title, other.title)

	def get_title(self):
		""" Return a string of the title, nicely formatted for XBMC list
		"""
		title = self.title
		return title

	def get_description(self):
		""" Return a string the program description, after running it through
			the descape.
		"""
		return utils.descape(self.description)

	def get_category(self):
		""" Return a string of the category. E.g. Comedy
		"""
		return utils.descape(self.category)

	def get_rating(self):
		""" Return a string of the rating. E.g. PG, MA
		"""
		return utils.descape(self.category)

	def get_duration(self):
		""" Return a string representing the duration of the program.
			E.g. 00:30 (30 minutes)
		"""
		return self.duration

	def get_date(self):
		""" Return a string of the date in the format 2010-02-28
			which is useful for XBMC labels.
		"""
		return self.date.strftime("%Y-%m-%d")

	def get_year(self):
		""" Return an integer of the year of publish date
		"""
		return self.date.year

	def get_season(self):
		""" Return an integer of the Series, discovered by a regular
			expression from the orginal title, unless its not available,
			then a 0 will be returned.
		"""
		if self.season is None:
			return self.get_year()
		return int(self.season)

	def get_thumbnail(self):
		""" Return a full URL of the thumbnail for the video.
			In many cases, a high-res URL is available, but we can't really
			tell if it exists or not without checking for a 200 response.
		"""
		thumbnail_standard = "http://bigpondvideo.com/web/images/content/%s" % self.thumbnail
		thumbnail_highres = thumbnail_standard.replace('89x50.jpg', '326x184.jpg')
		return thumbnail_highres

	def get_xbmc_list_item(self):
		""" Returns a dict of program information, in the format which
			XBMC requires for video metadata.
		"""
		info_dict = {
			'title': self.get_title(),
			'description': self.get_description(),
			'genre': self.get_category(), 
		}

		if self.duration: 
			info_dict['duration'] = self.get_duration()
		
		if self.description:
			info_dict['plot'] = self.get_description()

		return info_dict

	def make_xbmc_url(self):
		""" Returns a string which represents the program object, but in
			a format suitable for passing as a URL.
		"""
		url = "%s=%s" % ("id", self.id)
		url = "%s&%s=%s" % (url, "title", urllib.quote_plus(self.title))
		url = "%s&%s=%s" % (url, "description", urllib.quote_plus(self.description.encode('ascii','replace')))
		if self.duration:
			url = "%s&%s=%s" % (url, "duration", urllib.quote_plus(self.duration))
		url = "%s&%s=%s" % (url, "category", urllib.quote_plus(self.category))
		url = "%s&%s=%s" % (url, "rating", self.rating)
		url = "%s&%s=%s" % (url, "date", self.date.strftime("%d/%m/%Y %H:%M:%S"))
		url = "%s&%s=%s" % (url, "thumbnail", urllib.quote_plus(self.thumbnail))
		return url


	def parse_xbmc_url(self, string):
		""" Takes a string input which is a URL representation of the 
			program object
		"""
		d = utils.get_url(string)
		self.id = d['id']
		self.title = d['title']
		self.description = d['description']
		if d.has_key('duration'):
			self.duration = d['duration']
		self.category = d['category']
		self.rating = d['rating']
		timestamp = time.mktime(time.strptime(d['date'], '%d/%m/%Y %H:%M:%S'))
		self.date = datetime.date.fromtimestamp(timestamp)
		self.thumbnail = d['thumbnail']

