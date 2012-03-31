import sys
import re

import classes
import config
import utils

from pyamf.remoting.client import RemotingService

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

# Only use addon functions if we're on a new enough XBMC

def get_url(video_id):
	utils.log("Fetching video URL for content ID %s..." % video_id)
	client = RemotingService('http://afl.bigpondvideo.com/App/AmfPhp/gateway.php')
	service = client.getService('SEOPlayer')
	base_url = service.getMediaURL({'cid': video_id})
	video_url = quality_url(base_url)
	utils.log("Video URL found %s" % video_url)
	return video_url


def quality_url(base_url):
	# Only if we support addons will we allow this quality setting
	# or else we'll just hardcode it to high quality
	__addon__ = xbmcaddon.Addon()
	quality =  __addon__.getSetting('QUALITY')

	utils.log("Quality setting: %s" % quality)

	# 2m
	if base_url.endswith("2m.mp4"):
		if quality == '0':  	video_url = base_url.replace("2m.mp4", "172k.mp4")
		elif quality == '1': video_url = base_url.replace("2m.mp4", "1m.mp4")
	# 2M
	elif base_url.endswith("2M.mp4"):
		if quality == '0': 	video_url = base_url.replace("2M.mp4", "172K.mp4")
		elif quality == '1': video_url = base_url.replace("2M.mp4", "1M.mp4")
	# 2mb	
	elif base_url.endswith("2mb.mp4"):
		if quality == '0':   video_url = base_url.replace("2mb.mp4", "172kb.mp4")
		elif quality == '1': video_url = base_url.replace("2mb.mp4", "1mb.mp4")
	# 2MB	
	elif base_url.endswith("2MB.mp4"):
		if quality == '0':   video_url = base_url.replace("2MB.mp4", "172KB.mp4")
		elif quality == '1': video_url = base_url.replace("2MB.mp4", "1M.mp4")

	# High Quality
	if quality == '2':
		video_url = base_url

	return video_url

def play(url):
	v = classes.Video()
	v.parse_xbmc_url(url)

	# Show a dialog
	d = xbmcgui.DialogProgress()
	d.create(config.NAME, 'Starting video...')

	try:
		video_url = get_url(v.id)	
		listitem = xbmcgui.ListItem(label=v.get_title(), iconImage=v.get_thumbnail(), thumbnailImage=v.get_thumbnail())
		listitem.setInfo('video', v.get_xbmc_list_item())
	
		xbmc.Player().play(video_url, listitem)
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		message = utils.dialog_error("Unable to play video")
		d.ok(*message)
		utils.log_error();
