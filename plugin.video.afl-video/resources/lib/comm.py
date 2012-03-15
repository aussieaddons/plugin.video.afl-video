import os
import urllib2
import config
import re
import datetime, time
from BeautifulSoup import BeautifulStoneSoup
import classes

try: 
	import simplejson as json
except ImportError: 
	import json

def fetch_url(url):
	"""	Simple function that fetches a URL using urllib2.
		An exception is raised if an error (e.g. 404) occurs.
	"""
	print "AFL Video: Fetching URL: %s" % url
	http = urllib2.urlopen(urllib2.Request(url, None))
	return http.read()


def fetch_videos(url):
	data = fetch_url(url)
	index = json.loads(data)
	videos = []

	for v in index:
		new_video = classes.Video()
		new_video.title = v['name']
		new_video.thumbnail = v['thumbnail']

		# Python 2.4 hack - time module has strptime, but datetime does not until Python 2.5
		timestamp = time.mktime(time.strptime(v['date'], '%Y-%m-%d'))
		new_video.date = datetime.date.fromtimestamp(timestamp)

		new_video.urls = v['urls']
		videos.append(new_video)

	return videos


def fetch_matches():
	data = fetch_url(config.MATCHES_URL)
	index = json.loads(data)
	matches = []

	for m in index:
		new_match = classes.Match()
		new_match.id = m['id']
		new_match.title = m['name']
		new_match.thumbnail = config.SERVER + '/thumb/256x144/' + m['thumbnail']
		new_match.videos = m['videos']

		# Python 2.4 hack - time module has strptime, but datetime does not until Python 2.5
		timestamp = time.mktime(time.strptime(m['date'], '%Y-%m-%d'))
		new_match.date = datetime.date.fromtimestamp(timestamp)

		new_match.round = m['round']
		new_match.season = m['season']
		
		matches.append(new_match)

	return matches
