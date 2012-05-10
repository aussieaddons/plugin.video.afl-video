#
#    AFL Video XBMC Plugin
#    Copyright (C) 2012 Andy Botting
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
#    along with AFL Video.  If not, see <http://www.gnu.org/licenses/>.
#

import sys, re
import classes, config, utils
from pyamf.remoting.client import RemotingService
import xbmc, xbmcgui, xbmcplugin, xbmcaddon


def get_url(video_id):
	utils.log("Fetching video URL for content ID %s..." % video_id)
	client = RemotingService('http://afl.bigpondvideo.com/App/AmfPhp/gateway.php')
	service = client.getService('SEOPlayer')
	base_url = service.getMediaURL({'cid': video_id})
	utils.log("Base URL found: %s" % base_url)
	return base_url


def quality_url(base_url):
	# Only if we support addons will we allow this quality setting
	# or else we'll just hardcode it to high quality
	__addon__ = xbmcaddon.Addon()
	quality =  __addon__.getSetting('QUALITY')

	# High Quality
	if quality == config.QUAL_HIGH:
		video_url = base_url
	else:
		# 2m
		if base_url.endswith("2m.mp4"):
			if quality == config.QUAL_LOW:
				video_url = base_url.replace("2m.mp4", "172k.mp4")
			elif quality == config.QUAL_MED:
				video_url = base_url.replace("2m.mp4", "1m.mp4")
		# 2M
		elif base_url.endswith("2M.mp4"):
			if quality == config.QUAL_LOW:
				video_url = base_url.replace("2M.mp4", "172K.mp4")
			elif quality == config.QUAL_MED:
				video_url = base_url.replace("2M.mp4", "1M.mp4")
		# 2mb
		elif base_url.endswith("2mb.mp4"):
			if quality == config.QUAL_LOW:
				video_url = base_url.replace("2mb.mp4", "172kb.mp4")
			elif quality == config.QUAL_MED:
				video_url = base_url.replace("2mb.mp4", "1mb.mp4")
		# 2MB
		elif base_url.endswith("2MB.mp4"):
			if quality == config.QUAL_LOW:
				video_url = base_url.replace("2MB.mp4", "172KB.mp4")
			elif quality == config.QUAL_MED:
				video_url = base_url.replace("2MB.mp4", "1MB.mp4")
		else:
			utils.log("Unknown video quality, playing default")
			video_url = base_url

	return video_url


def play(url):
	# Show a dialog
	d = xbmcgui.DialogProgress()
	d.create(config.NAME, '')
	d.update(20, 'Fetching video parameters...')

	v = classes.Video()
	v.parse_xbmc_url(url)

	try:
		d.update(40, 'Fetching video URL...')
		base_url = get_url(v.id)

		d.update(60, 'Fetching video URL...')
		video_url = quality_url(base_url)

		d.update(80, 'Building playlist...')
		listitem = xbmcgui.ListItem(label=v.get_title(), iconImage=v.get_thumbnail(), thumbnailImage=v.get_thumbnail())
		listitem.setInfo('video', v.get_xbmc_list_item())
	
		d.update(99, 'Starting video...')
		xbmc.Player().play(video_url, listitem)
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		message = utils.dialog_error("Unable to play video")
		d.ok(*message)
		utils.log_error();
